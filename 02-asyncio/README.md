# Асинхронность

<a name="index"></a>
* [История асинхронной разработки на python](#timeline)
  * [Сравнение корутин tornado, старых корутин asyncio и нативных корутин](#coroutines_history)
* [Асинхронность на уровне ОС](#os)
* [Библиотека asyncio](#asyncio)
* [Awaitable-объекты](#awaitable)
  * [Корутины](#coroutines-objects)
  * [Таски](#tasks)
  * [Фьючи](#futures)
* [Реализации event loop для asyncio](#event_loop)
  * [Стандартный](#default_event_loop)
  * [uvloop](#uvloop)
  * [tokio](#tokio_event_loop)
* [Генераторы и корутины](#coroutines)
* [Оптимизация асинхронных http-серверов](#http_servers)
* [Дополнительные материалы](#resources)

<a name="timeline"></a>
## История асинхронной разработки на python [^](#index "к оглавлению")

| Год  | События |
| ---- | ------- |
| 2002 | появление [Twisted](https://github.com/twisted/twisted), event loop - "Reactor". Позже появились свои Future-объекты, называемые `Deferred`, корутины `@inlineCallbacks`, возможность выполнить задачу в пуле потоков `deferToThread(func)` |
| 2009 | появление библиотеки [gevent](http://www.gevent.org/). Она позволяла оборачивать задачи в "зеленые потоки" (интерфейс похож на модуль `threading`, однако не использует потоки ОС) и выполнять их на event loop (на `libev` или `libuv`). При переключении гринтредов заменялся системный стек. Недостатки: приходилось патчить методы (`monkey.patch_all()`) и yield не поддерживался |
|      | появление [Tornado](https://github.com/tornadoweb/tornado), которую мы используем в настоящее время | 
| 2012 | Гвидо ван Россум написал первую, пробную, [версию asyncio](https://github.com/python/asyncio), пока в качестве отдельного пакета под python 3.3. При дальнейшей разработке core-разработчики python консультировались с создателями Twisted и Tornado и переняли все хорошее, что там было | 
| 2013 | появление в Tornado 3 корутин `@gen.coroutine`, используемых с `yield` и базирующихся на генераторах, для более удобного (по сравнению с коллбечным) написания кода [*](#coroutines_history) |
|      | Андрей Светлов выпустил первую версию библиотеки [aiohttp](https://github.com/aio-libs/aiohttp) - реализацию http-протокола для `asyncio`. В стандартную библиотеку python `aiohttp` решили не добавлять |
| 2014 | asyncio стала частью стандартной библиотеки python 3.4, с корутинами на декораторах `@asyncio.coroutine`, используемых с `yield from` [*](#coroutines_history) |
|      | в Tornado 3 появилась экспериментальная поддержка asyncio |
| 2015 | в python 3.5 появился новый синтакис для корутин - `async` и `await` [*](#coroutines_history), а также инструкции `async with` и `async for`. Такие корутины работают быстрее, чем старые, с декоратором. Также добавили метод `loop.create_task()` |
| 2016 | появление поддержки event loop из asyncio в Twisted |
|      | в python 3.6 появилась поддержка асинхронных генераторов (можно использовать `yield` в корутинах), async comprehensions |
|      | появление ультра-быстрого веб-фреймворка [sanic](https://sanicframework.org/), который является реализацией http-протокола для `asyncio` |
| 2018 | в Tornado 5 стали использоваться Futures, Tasks и event loop из asyncio вместо своих, поддерживаются теперь нативные корутины `async def` |
|      | в python 3.7 методы из asyncio сделали более удобными для использования (например, добавили `asyncio.run()`) и улучшили производительность, добавили `contextvars` - аналог thread-local переменных для асинхронного кода |
| 2019 | в Tornado 6 улучшена поддержка asyncio, нативных корутин, выпилены коллбеки из большинства методов |

Библиотеки Twisted, Gevent и Tornado, хоть и не совсем заброшены (версии новые выходят), но в новых проектах уже не используются, так как все необходимое,
кроме разве что реализации http-протокола, уже есть в стандартной библиотеке в модуле [asyncio](https://docs.python.org/3/library/asyncio.html).
Современные Twisted и Tornado также имеют поддержку asyncio.

<a name="coroutines_history"></a>
### Сравнение корутин tornado, старых корутин asyncio и нативных корутин

<table>
<thead>
<tr>
    <th>Корутины tornado</th>
    <th>Старые корутины asyncio</th>
    <th>Нативные корутины</th>
</tr>
</thead>
<tr>
<td>
    Базируются на генераторах. Используются совместно с `yield`. После добавления в tornado 5
    поддержки нативных корутин их использование не рекомендуется.
    [Документация](https://www.tornadoweb.org/en/stable/guide/coroutines.html)

```python
from tornado import gen

@gen.coroutine
def a():
    b = yield c()
    return b
```

</td>
<td>
    Появились в версии 3.4.
    Базируются на генераторах. Используются совместно с `yield from` (в отличие от корутин tornado).
    [Документация](https://docs.python.org/3.4/library/asyncio-task.html#coroutines). После появления в версии 3.5
    нативных корутин их использование не рекомендуется, и в версии 3.10 они будут выпилены.

```python
import asyncio

@asyncio.coroutine
def a():
    b = yield from c()
    return b
```

</td>
<td>
    Появились в версии 3.5.
    Подвид генераторов. Используются совместно с `await`. Часть языка, а не какой-либо библиотеки. Хорошо оптимизированы и рекомендуются к использованию.

```python
async def a():
    b = await c()
    return b
```
</td>
</tr>
</table>

Приложения на корутинах tornado, а также приложения на старых корутинах asyncio работают 
медленнее, чем приложения на нативных корутинах. Рекомендуеся использовать исключительно последние.

<a name="os"></a>
## Асинхронность на уровне ОС* [^](#index "к оглавлению")

Все перечисленные выше библиотеки, Asyncio, Twisted, Gevent и Tornado, основаны на одном механизме - неблокирующем вводе-выводе и мультиплексировании, как
и множество подобных проектов, например, nodejs, браузеры, nginx, qt, gtk, 
netty ([NioEventLoop.java](https://github.com/netty/netty/blob/4.1/transport/src/main/java/io/netty/channel/nio/NioEventLoop.java#L437-L537)), 
[tokio](https://github.com/tokio-rs/tokio), [evio](https://github.com/tidwall/evio).

> `*` Здесь и далее мы не рассматриваем другой тип асинхронности, основанный только на пуле потоков и применяемый
> в C#, kotlin, java (CompletableFuture). У нас же пул потоков - лишь вспомогательное решение для ряда операций (не pollable).

Все подобные приложения используют под капотом примерно такой код (на linux, для mac же используется kqueue):

```c
int ep = epoll_create(1);
struct epoll_event new_ev;
new_ev.data.fd = server;
new_ev.events = EPOLLIN;
epoll_ctl(ep, EPOLL_CTL_ADD, server, &new_ev);
while(1) {
    if (epoll_wait(ep, &new_ev, 1, 2000) == 0) {
        printf("Timeout\n");
            continue;
    }
    if (new_ev.data.fd == server) {
        int client_sock = accept(server, NULL, NULL);
        printf("New client\n");
        new_ev.data.fd = client_sock;
        new_ev.events = EPOLLIN;
        epoll_ctl(ep, EPOLL_CTL_ADD, client_sock, &new_ev);
    } else {
        printf("Interact with fd %d\n", (int)new_ev.data.fd);
        if (interact(new_ev.data.fd) == 0) {
            printf("Client disconnected\n");
            close(new_ev.data.fd);
            epoll_ctl(ep, EPOLL_CTL_DEL, new_ev.data.fd, NULL);
        } 
    }
} 
close(ep);
```

Разберем подробнее присутствующие в этом коде системные вызовы:
* `int epoll_create(int size)`, `int epoll_create1(int flags)` - создает экземпляр epoll и возвращает указывающий на него файловый дескриптор
* `int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event);` - добавляет, изменяет, удаляет дескрипторы из списка интереса экземпляра epoll. В объекте event содержится тип нужного события и пользовательские данные
* `int epoll_wait(int epfd, struct epoll_event *events, int maxevents, int timeout)` - ожидает события на экземпляре epoll, возвращает произошедшие отслеживаемые события
* `close(int fd)` - закрывает дескриптор

Последовательность операций:
1. Создаем экземпляр epoll
2. Делаем все дескрипторы, которые нужно отслеживать, неблокирующими
3. Формируем список интереса epoll с помощью вызова `epoll_ctl()`, добавляя и удаляя из него эти дескрипторы
3. В цикле обрабатываем события ввода/вывода:
   * извлекаем список готовых дескрипторов, используя `epoll_wait()`
   * выполняем ввод/вывод для каждого готового дескриптора, пока соответствующий системный вызов
   (например, readQ, writeQ, recvQ, sendQ или acceptQ) не вернет ошибку EAGAIN или EWOULDBLOCK

### Pollable-операции: 
* net, dgram, http, tls, https
* child process pipes
* stdin, stdout, stderror
* таймауты `epoll_wait(..., int timeout)`
* сигналы

### Не pollable-операции:
* все, что касается работы с файловой системой
* работа с dns (а именно `dns.lookup()`, вызывающий блокирующую `getaddrinfo()`, остальные методы `dns.*` - не блокирующие) 
Такие операции выполняются вне event loop'а, на пуле потоков, и сообщают ему, когда работа будет завершена 
  (используя `eventfd` или `self-pipe` - создается в потоке, слушается лупом)

`epoll_wait` - блокирующий вызов (до того момента, когда какие-либо дескрипторы из списка наблюдаемых,
будут готовы на чтение или на запись). Посмотрим на реальном примере: запустим пример асинхронного веб-сервера [async_server_example.py](async_server_example.py) 
на sanic через `strace`, а затем сделаем к нему запрос с другой консоли: `curl localhost:8080`.

```console
vera@vera:~$ strace -e epoll_create1,epoll_wait,epoll_ctl python3 async_server_example.py  >> /dev/null
--- SIGCHLD {si_signo=SIGCHLD, si_code=CLD_EXITED, si_pid=7144, si_uid=2000, si_status=0, si_utime=0, si_stime=0} ---
epoll_create1(EPOLL_CLOEXEC)            = 3
epoll_ctl(3, EPOLL_CTL_ADD, 9, {EPOLLIN, {u32=4294967295, u64=4294967295}}) = 0
epoll_ctl(3, EPOLL_CTL_DEL, 9, 0x7ffcb2e0e3cc) = 0
epoll_ctl(3, EPOLL_CTL_DEL, 9, 0x7ffcb2e0e3ec) = -1 ENOENT (No such file or directory)
epoll_ctl(3, EPOLL_CTL_ADD, 6, {EPOLLIN, {u32=6, u64=6}}) = 0
epoll_ctl(3, EPOLL_CTL_ADD, 8, {EPOLLIN, {u32=8, u64=8}}) = 0
epoll_ctl(3, EPOLL_CTL_ADD, 9, {EPOLLIN, {u32=9, u64=9}}) = 0
epoll_wait(3, [{EPOLLIN, {u32=8, u64=8}}], 1024, 0) = 1
epoll_wait(3, [{EPOLLIN, {u32=8, u64=8}}], 1024, 0) = 1
epoll_wait(3, [], 1024, 0)              = 0
epoll_ctl(3, EPOLL_CTL_ADD, 11, {EPOLLIN, {u32=11, u64=11}}) = 0
epoll_wait(3, [], 1024, 0)              = 0
epoll_wait(3, [{EPOLLIN, {u32=11, u64=11}}], 1024, -1) = 1
epoll_ctl(3, EPOLL_CTL_ADD, 13, {EPOLLIN, {u32=13, u64=13}}) = 0
epoll_wait(3, [{EPOLLIN, {u32=13, u64=13}}], 1024, 60000) = 1
epoll_wait(3, [], 1024, 0)              = 0
epoll_wait(3, [{EPOLLIN, {u32=13, u64=13}}], 1024, 4999) = 1
epoll_ctl(3, EPOLL_CTL_DEL, 13, 0x7ffcb2e0debc) = 0
epoll_wait(3, [], 1024, 0)              = 0
epoll_wait(3, # ... ждем новые события
```

<a name="asyncio"></a>
## Библиотека asyncio [^](#index "к оглавлению")

Асинхронная разработка в питоне базируется на [event loop'е](#event_loop) и [awaitable-объектах](#awaitable).

Для удобства библиотека [asyncio](https://docs.python.org/3/library/asyncio.html) была разделена 
на [высокоуровненое](https://docs.python.org/3/library/asyncio-api-index.html) (пользовательский код) и 
[низкоуровневое](https://docs.python.org/3/library/asyncio-llapi-index.html) апи (код библиотек).

<a name="awaitable"></a>
## Awaitable-объекты [^](#index "к оглавлению")
В питоне существует три типа awaitable-объектов (имеют метод `__await__` и могут использоваться с инструкцией `await`): корутины, фьючи, таски.

<a name="coroutines-objects"></a>
### Корутины [^](#index "к оглавлению")
* Есть функции-корутины и объекты-корутины, получаемые путем вызова функций-корутин
* Фактически, на уровне интерпретатора, это подвид генераторов
* Для выполнения на event loop'е преобразуется в Task/Future

<a name="futures"></a>
### Фьючи [^](#index "к оглавлению")
* Future: код [base_futures.py](https://github.com/python/cpython/blob/3.9/Lib/asyncio/base_futures.py), [futures](https://github.com/python/cpython/blob/3.9/Lib/asyncio/futures.py#L29)
* Имеют три состояния: PENDING, CANCELLED, FINISHED. Важные методы: cancel, result, exception, set_result, set_exception, add_done_callback, remove_done_callback
* Низкоуровневый awaitable-объект, представляющий результат асинхронной операции
* Обычно не используется в пользовательском коде
* Если мы авейтим фьючу, то дожидаемся когда у нее появится результат или исключение
* Используется для того, чтобы коллбечный код мог использоваться с async-await
* Некоторые функции из библиотеки asyncio, например `loop.run_in_executor()`, возвращают фьючи
* Создаются вызовом `loop.create_future()`

<a name="tasks"></a>
### Таски [^](#index "к оглавлению")
* Task: наследуются от Future, код [base_tasks.py](https://github.com/python/cpython/blob/3.9/Lib/asyncio/base_tasks.py), [tasks.py](https://github.com/python/cpython/blob/3.9/Lib/asyncio/tasks.py#L239-L324)
* Если мы авейтим корутину, она под капотом неявно преобразается в таску
* В отличие от Future, имеют дополнительный метод `__step`, в котором у оборачиваемой корутины делается `result = coro.send(None)`
* Вручную можно создать таску через `asyncio.create_task`
* После создания таска сразу ставится на выполнение на event loop
* Таску можно авейтить ниже в коде либо не авейтить вообще
* Если таску не авейтить - фактически это будет выполнение задачи в фоновом режиме
* У таски есть метод `.cancel()` и ее можно отменить
* Таска наследется от Future, и у нее так же есть метод `.add_done_callback`

<table>
<thead>
<tr>
    <th>Корутины</th>
    <th>Futures</th>
    <th>Tasks</th>
</tr>
</thead>
<tr>
<td>

```python
>>> import asyncio

>>> async def main():
... print('hello')
... await asyncio.sleep(1)
... print('world')
    
>>> coro = main()  
<stdin>:1: RuntimeWarning: coroutine 'main' was never awaited
Object allocated at (most recent call last):
  File "<stdin>", lineno 1
  
>>> coro
<coroutine object main at 0x104709740>
    
>>> dir(coro)
['__await__', '__class__', '__del__', '__delattr__', '__dir__', 
'__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', 
'__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', 
'__lt__', '__name__', '__ne__', '__new__', '__qualname__', 
'__reduce__', '__reduce_ex__', '__repr__', '__setattr__', 
'__sizeof__', '__str__', '__subclasshook__', 'close', 'cr_await', 
'cr_code', 'cr_frame', 'cr_origin', 'cr_running', 'send', 'throw']

>>> asyncio.run(main())
hello
world
```

</td>
<td>

```python
>>> import asyncio

>>> async def set_after(fut, delay, value):
...    await asyncio.sleep(delay)
...    fut.set_result(value)

>>> fut = None

>>> async def main():
...    loop = asyncio.get_running_loop()
...    global fut
...    fut = loop.create_future()
...    loop.create_task(set_after(fut, 1, '... world'))
...    print('hello ...')
...    print(await fut)

>>> asyncio.run(main())

>>> fut
<Future finished result='... world' created 
at ....python3.9/asyncio/base_events.py:424>

>>> dir(fut)
['__await__', '__class__', '__class_getitem__', '__del__', 
'__delattr__', '__dir__', '__doc__', '__eq__', '__format__', 
'__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', 
'__init_subclass__', '__iter__', '__le__', '__lt__', '__ne__', 
'__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', 
'__sizeof__', '__str__', '__subclasshook__', '_asyncio_future_blocking',
 '_callbacks', '_cancel_message', '_exception', '_log_traceback', 
 '_loop', '_make_cancelled_error', '_repr_info', '_result', 
 '_source_traceback', '_state', 'add_done_callback', 'cancel', 
 'cancelled', 'done', 'exception', 'get_loop', 'remove_done_callback', 
 'result', 'set_exception', 'set_result']
```
</td>
<td>

```python
>>> import asyncio

>>> async def nested():
...    return 42

>>> task = None

>>> async def main():
...    global task
...    task = asyncio.create_task(nested())
...    await task

>>> asyncio.run(main())

>>> task
<Task finished name='Task-6' coro=<nested() done, defined at <stdin>:1> 
result=42 created at ....python3.9/asyncio/tasks.py:361>

>>> dir(task)
['__await__', '__class__', '__class_getitem__', '__del__', 
'__delattr__', '__dir__', '__doc__', '__eq__', '__format__', 
'__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', 
'__init_subclass__', '__iter__', '__le__', '__lt__', '__ne__', 
'__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', 
'__sizeof__', '__str__', '__subclasshook__', '_asyncio_future_blocking', 
'_callbacks', '_cancel_message', '_coro', '_exception', '_fut_waiter', 
'_log_destroy_pending', '_log_traceback', '_loop', '_make_cancelled_error', 
'_must_cancel', '_repr_info', '_result', '_source_traceback', '_state', 
'add_done_callback', 'cancel', 'cancelled', 'done', 'exception', 'get_coro', 
'get_loop', 'get_name', 'get_stack', 'print_stack', 'remove_done_callback', 
'result', 'set_exception', 'set_name', 'set_result']
```

</td>
</tr>
</table>

Корутины (async-await синтаксис) - это часть языка, а не библиотеки asyncio, что позволило написать альтернативные 
asyncio любопытные библиотеки: [curio](https://github.com/dabeaz/curio) от Девида Бизли и 
[trio](https://github.com/python-trio/trio) от Натаниэля Смита.
  
### Несколько примеров

* [Последовательное выполнение](01-sequential.py)
* [Параллельное выполнение](02-gather.py)
* [Параллельное выполнение с условием](03-wait.py)
* [Выполнение с таймаутом](04-wait_for.py)
* [Итерация по мере выполнения](05-as_completed.py)
* [Работа с задачами](06-create_task.py)
* [Выполнение блокирующих io-операций на пуле потоков](07-to_thread.py)
* [Выполнение колбека на следующей итерации цикла](09-call_soon.py)
* [Выполнение колбека через некоторое время](08-call_later.py)
* [Запланировать выполнение колбека на точное время](10-call_at.py)

<a name="event_loop"></a>
## Реализации event loop для asyncio [^](#index "к оглавлению")
Для использования с библиотекой asyncio event loop должен реализовывать 
[методы класса `AbstractEventLoop`](https://github.com/python/cpython/blob/8b795ab5541d8a4e69be4137dfdc207714270b77/Lib/asyncio/events.py#L204):

* run_forever()
* run_until_complete()
* stop()
* is_running()
* is_closed()
* close()
* shutdown_asyncgens()
* shutdown_default_executor()
* call_soon()
* call_later()
* call_at()
* time()
* create_future()
* create_task()
* call_soon_threadsafe()
* run_in_executor()
* set_default_executor()
* getaddrinfo()
* getnameinfo()
* create_connection()
* create_server()
* sendfile()
* start_tls()
* create_unix_connection()
* create_unix_server()
* create_datagram_endpoint()
* connect_read_pipe()
* connect_write_pipe()
* subprocess_shell()
* subprocess_exec()
* add_reader()
* remove_reader(self, fd)
* add_writer()
* remove_writer()
* sock_recv()
* sock_recv_into()
* sock_sendall()
* sock_connect()
* sock_accept()
* sock_sendfile()
* add_signal_handler()
* remove_signal_handler()
* set_task_factory()
* get_task_factory()
* get_exception_handler()
* set_exception_handler()
* default_exception_handler()
* call_exception_handler()
* get_debug()
* set_debug()

<a name="default_event_loop"></a>
### Стандартный [^](#index "к оглавлению")
Написан на питоне. Используется по умолчанию.

* [Документация](https://docs.python.org/3/library/asyncio-eventloop.html)
* Код [events.py](https://github.com/python/cpython/blob/3.9/Lib/asyncio/events.py) `->` 
  [base_events.py](https://github.com/python/cpython/blob/3.9/Lib/asyncio/base_events.py#L1815-L1891) `->`
  [selector_events.py](https://github.com/python/cpython/blob/3.9/Lib/asyncio/selector_events.py)

<a name="uvloop"></a>
### uvloop [^](#index "к оглавлению")
Написан Юрием Селивановым с использованием libuv в 2016 г. В настоящее время часто используется в продакшене, даже в крупных
компаниях. По сравнению со стандартным дает прирост производительности в 2-4 раза 
(по данным [статьи](http://magic.io/blog/uvloop-make-python-networking-great-again/)), на реальных проектах результат скромнее,
но тоже ощутим (согласно замерам, проведенным в компании Rambler, ~30%).

* Биндинги: https://github.com/MagicStack/uvloop ([loop](https://github.com/MagicStack/uvloop/blob/master/uvloop/loop.pyx))
* Сама сишная либа: https://libuv.org/, https://github.com/libuv/libuv, 
  [loop](https://github.com/libuv/libuv/blob/c9406ba0e3d67907c1973a71968b89a6bd83c63c/src/unix/core.c#L365)
* [хорошая статья](https://habr.com/ru/post/336498/), [видео](https://www.youtube.com/watch?v=7f787SsgknA) про event loop nodejs и libuv

Как использовать:

```python
import asyncio
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
```

<a name="tokio_event_loop"></a>
### tokio [^](#index "к оглавлению")
Написан с использованием tokio.rs в 2017 г., с 2018 г. проект не поддерживается более.

Как использовать:

```python
import asyncio
import tokio

asyncio.set_event_loop_policy(tokio.EventLoopPolicy())
```
* Биндинги: https://github.com/PyO3/tokio ([loop](https://github.com/PyO3/tokio/blob/master/src/event_loop.rs))
* Сама библиотека на rust: https://tokio.rs/, https://github.com/tokio-rs/tokio

<a name="coroutines"></a>
## Генераторы и корутины [^](#index "к оглавлению")

Вообще, корутины появились довольно давно и используются в настоящее время в нескольких языках (c#, kotlin, rust, python, js, c++),
чтобы писать асинхронный код в синхронном стиле. Синтаксис `async`-`await` впервые появился в C# 5.0 (2012 г.).

В питоне корутины основаны на механизме генераторов, используют их способность приостанавливать свое выполнение и возвращать управление
в вызывающий код, а затем возобновлять работу с воссоздпным окружением.

<table>
<thead>
<tr>
    <th>yield</th>
    <th>yield from</th>
</tr>
</thead>
<tr>
<td>
    Сложный генератор, давайте его порефакторим и выделим какую-то часть в другой,
вложенный, генератор.

```python
def test_gen():
    val = yield 1
    # -----
    yield 2
    yield 3
    yield 4
    # -----
    yield 5
    return 'returned by gen'

gen = test_gen()
try:
    while True:
        print(next(gen))  # = send(None)
except StopIteration as e:
    print(e)

# 1
# 2
# 3
# 4
# 5
# returned by gen
```

</td>
<td>
    Выделяем вложенный генератор и вызываем его при помощи инструкции `yield from`, 
которая будет прокручивать вложенный генератор, как в примере слева, и пробрасывать данные,
переданные методом `send(smth)`, из родительского во вложенный,
прокрутит вложенный генератор до конца и вернет значение из StopIteration, 
которое мы сохраним в переменную `a`.
    

```python
def test_subgen():
    yield 2
    yield 3
    yield 4
    return 'returned by sub_gen'
    
def test_gen():
    yield 1
    a = yield from test_subgen()
    print(a)
    yield 5
    return 'returned by gen'

gen = test_gen()
try:
    while True:
        print(next(gen))  # = send(None)
except StopIteration as e:
    print(e)

# 1
# 2
# 3
# 4
# returned by sub_gen
# 5
# returned by gen
```

</td>
</tr>
</table>

<table>
<thead>
<tr>
    <th>Функции</th>
    <th>Генераторы</th>
    <th>Корутины</th>
</tr>
</thead>
<tr>
<td>
    Обычная функция

```python
def some_name(arg1, arg2):
    return arg1 + arg2
```

</td>
<td>
    Функция-генератор

```python
def some_name(arg1, arg2):
    yield arg1
    yield arg2
    return arg1 + arg2
```

</td>
<td>
    Функция-корутина

```python
async def some_name(arg1, arg2):
    await asyncio.sleep(arg1)
    await asyncio.sleep(arg2)
    return arg1 + arg2
```
</td>
</tr>
<tr>
<td>

```python
>>> type(some_name)
<class 'function'>
```

</td>
<td>

```python
>>> type(some_name)
<class 'function'>
```

</td>
<td>

```python
>>> type(some_name)
<class 'function'>
```

</td>
</tr>



<tr>
<td>
возвращается значение

```python
>>> some_name(1,2)
3
```
</td>
<td>
возвращается объект генератора

```python
>>> some_name(1,2)
<generator object some_name at 0x10d48b2e0>
```
</td>
<td>
возвращается объект корутины

```python
>>> some_name(1,2)
<coroutine object some_name at 0x10dfa0a40>
```
</td>
</tr>
<tr>
<td>

```python
>>> type(some_name(1,2))
<class 'int'>
```

</td>
<td>

```python
>>> type(some_name(1,2))
<class 'generator'>
```

</td>
<td>

```python
>>> type(some_name(1,2))
<stdin>:1: RuntimeWarning: coroutine 'some_name' was never awaited
Object allocated at (most recent call last):
File "<stdin>", lineno 1
<class 'coroutine'>
```

</td>
</tr>

<tr>
<td></td>
<td>

```python
>>> dir(some_name(1,2))
# лишнее вырезала
['__iter__', '__next__', 'close', 
 'gi_code', 'gi_frame', 'gi_running', 
 'gi_yieldfrom', 'send', 'throw']
```

имеет интерфейс итератора
</td>
<td>

```python
>>> dir(some_name(1,2))
# лишнее вырезала
['__await__', 'close', 'cr_await', 
 'cr_code', 'cr_frame', 'cr_origin', 
 'cr_running', 'send', 'throw']
```

awaitable-объект
</td>
</tr>


<tr>
<td></td>
<td>

локальные переменные на каждой итерации

```python
>>> def some_name(arg1, arg2):
...    x = 0
...    yield arg1
...    x += arg1
...    yield arg2
...    x += arg2
...    return arg1 + arg2

>>> gen = some_name(1,2)
>>> print(gen.gi_frame.f_locals)
>>> gen.send(None)  # то же самое, что и next(gen)
>>> print(gen.gi_frame.f_locals)
>>> gen.send(None)  # то же самое, что и next(gen)
>>> print(gen.gi_frame.f_locals)
>>> gen.send(None)  # то же самое, что и next(gen)

{'arg1': 1, 'arg2': 2}
{'arg1': 1, 'arg2': 2, 'x': 0}
{'arg1': 1, 'arg2': 2, 'x': 1}
Traceback (most recent call last):
    File "/Users/vera/dev/awaitable1.py", line 93, in <module>
        gen.send(None)
StopIteration: 3
```
возвращаемое значение находится в объекте исключения `StopIteration`

</td>
<td>

локальные переменные на каждой итерации

```python
>>> async def some_name(arg1, arg2):
...     x = 0
...     await other_coro(arg1)
...     x += arg1
...     await other_coro(arg2)
...     x += arg2
...     return arg1 + arg2

>>> gen = some_name(1,2)
>>> print(gen.cr_frame.f_locals)
>>> gen.send(None)
>>> print(gen.cr_frame.f_locals)
>>> gen.send(None)
>>> print(gen.cr_frame.f_locals)
>>> gen.send(None)

{'arg1': 1, 'arg2': 2}
{'arg1': 1, 'arg2': 2, 'x': 0}
{'arg1': 1, 'arg2': 2, 'x': 1}
Traceback (most recent call last):
    File "/Users/vera/dev/awaitable1.py", line 93, in <module>
        gen.send(None)
StopIteration: 3
```

возвращаемое значение находится в объекте исключения `StopIteration`.
такой же генератор по сути, только вместо `gi_frame` - `cr_frame`.
`gen.send(None)` в реальной жизни мы не делаем руками, его вызывает сам event loop.
</td>
</tr>


<tr>
<td></td>
<td>

```python
>>> def coro():
...     y = yield from a
...
>>> dis.dis(coro)
2           0 LOAD_GLOBAL              0 (a)
            2 GET_YIELD_FROM_ITER
            4 LOAD_CONST               0 (None)
            6 YIELD_FROM
            8 STORE_FAST               0 (y)
            10 LOAD_CONST              0 (None)
            12 RETURN_VALUE
```

</td>
<td>

```python
>>> async def async_coro():
...     y = await a
... 
>>> dis.dis(async_coro)
2           0 LOAD_GLOBAL              0 (a)
            2 GET_AWAITABLE
            4 LOAD_CONST               0 (None)
            6 YIELD_FROM
            8 STORE_FAST               0 (y)
            10 LOAD_CONST              0 (None)
            12 RETURN_VALUE
```

</td>
</tr>

<tr>
<td></td>
<td></td>
<td></td>
</tr>

<tr>
<td></td>
<td></td>
<td></td>
</tr>

</table>

<a name="http_servers"></a>
## Оптимизация асинхронных http-серверов [^](#index "к оглавлению")

В библиотеке asyncio есть много чего, нет только реализации http-протокола (придется дополнительно устанавливать
одну из библиотек - aiohttp, sanic, tornado или подобные), 
которая подразумевала бы работу с объектами HTTPRequest (полученным парсингом строки запроса) и HTTPResponse 
(который надо преобразовать в строку ответа, xml или json). 

Например, в нижеприведенном запросе http-сервер должен распарсить большую строку от клиента и выделить из нее
запрашиваемый метод и путь, query- и path-параметры, заголовки и тело в json, xml или form-параметрах.

```console
vera@vera$ ncat -C --ssl github.com 443
POST /
User-Agent: vera

data=1&n=2

HTTP/1.1 400 Bad Request
Cache-Control: no-cache

{
    "error": 400
}
```

Чтобы отдать большую строку ответа, нужно сформировать ее из объекта, содержащего возвращаемый код, заголовки, тело ответа в json, xml или html.

Строковые операции всегда дорогие, а для асинхронного приложения это критично. 
В tornado парсинг написан на питоне https://github.com/tornadoweb/tornado/blob/master/tornado/httputil.py,
в aiohttp на cython https://github.com/aio-libs/aiohttp/blob/master/aiohttp/_http_parser.pyx,
[sanic](https://github.com/sanic-org/sanic/blob/master/setup.py#L87-L89) же использует, помимо uvloop, 
[httptools](https://github.com/MagicStack/httptools) - биндинги для http-парсера, используемого в nodejs, а также 
[ujson](https://github.com/ultrajson/ultrajson) для работы с json - все это написано на C.

Tornado проигрывает последним двум серверам не только из-за большого количества легаси-кода, который до сих пор остается
в библиотеке, но также и потому, что нет таких оптимизаций, а Sanic по результатам некоторых тестов показывает наилучшие результаты.

<a name="resources"></a>
## Дополнительные материалы [^](#index "к оглавлению")

* [Алексей Кузьмин, ДомКлик «Асинхронность изнутри»](https://www.youtube.com/watch?v=pZkerqks43Y)
* [Конкурентность в Питоне с нуля. Вживую. Девид Бизли]( https://www.youtube.com/watch?v=ys8lW8eQaJQ)
* [Что внутри у питона: откуда быть пошел async (про генераторы и корутины). З. Обуховская](https://www.youtube.com/watch?v=GX7AUAwpQ4I)
* [Лекция async/await курса Программирование на python ot CSC](https://www.youtube.com/watch?v=x6JZmBK2I8Y)
* [Злата Обуховская, Nvidia «Structured Concurrency. Что не так с асинхронностью в питоне?»](https://www.youtube.com/watch?v=NmWzt7VdTgA)
* [Node's Event Loop From the Inside Out by Sam Roberts, IBM](https://www.youtube.com/watch?v=P9csgxBgaZ8)
* [Неблокирующие IO-операции. Мультиплексирование: select, epoll, kqueue. Курс по системному программированию. В. Шпилевой](https://www.youtube.com/watch?v=Sk8gl8SY_GY&t=2896)
* [Курс лекций "Основы асинхронности в Python" Олега Молчанова](https://www.youtube.com/watch?v=ZGfv_yRLBiY&list=PLlWXhlUMyooawilqK4lPXRvxtbYiw34S8)
* [Guide to Concurrency in Python with Asyncio, Mark McDonnell](https://www.integralist.co.uk/posts/python-asyncio/)
* [Другие материалы по теме](https://github.com/vera-l/python-resources#async)
