# Конкурентность и параллелизм в питоне

<a name="index"></a>
* [Теория](#theory)
* [Измерения](#tests)
  * [Тестовая машина #1 (10 ядер)](#cpu1)
  * [Тестовая машина #2 (2 ядра)](#cpu2)
  * [Тестовая машина #3 (1 ядро)](#cpu3)
* [Выводы](#conclusion)

<a name="theory"></a>
## Теория [^](#index "к оглавлению")

### Многозадачность

* Вытесняющая - выполнение задачи прерывается извне и ресурсы передаются другой задаче (threading, multiprocessing)
* Кооперативная - одна задача передает управление другой (async)

### Конкурентность и параллелизм

* Конкурентное выполнение - это когда несколько задач одновременно находятся в работе (в незавершенном состоянии) и 
понемногу продвигаются в прогрессе (async, процессы и потоки для 1 ядра, потоки для cpu-задач в питоне)
* Параллелизм - все задачи выполняются в один и тот же момент времени (процессы и потоки (для IO) в случае нескольких ядер)

### Процессы
* https://docs.python.org/3/library/multiprocessing.html
* https://docs.python.org/3/library/os.html#os.fork

### Потоки
* https://docs.python.org/3/library/threading.html

### Пул потоков или процессов
* https://docs.python.org/3/library/concurrent.futures.html
* https://docs.python.org/3/library/multiprocessing.html#module-multiprocessing.pool

### Asyncio
* https://docs.python.org/3/library/asyncio.html

<a name="tests"></a>
## Измерения [^](#index "к оглавлению")

Проведем ряд тестов для того чтобы показать каждый аспект проблемы выбора технологического решения. 

В качестве примера io-bound задачи возьмем получение ресурсов из списка по сети, 
cpu-bound - вычисление чисел Фибоначчи из списка сравнимой по времени с io-задачей. 

Попробуем максимально ускорить задачу различными способами - используя потоки, процессы, пул потоков,
пул процессов и асинхронность, сравниваем с последовательным выполнением.
Также, пробуем сочетать io- и cpu-bound задачи и ускорять такую систему.

Сравнивать между собой нужно будет каждый тип задач (`io`, `cpu`, `io+cpu` - обозначены префиксами).

Также, проверим, зависят ли возможности по распараллеливанию задач от железа, для этого
запустим набор тестов на трех разных машинах.

Замеры производились с помощью `/usr/bin/time -v` для linux и `/usr/bin/time -l` для mac.

<a name="cpu1"></a>
### Тестовая машина #1 (10 ядер) [^](#index "к оглавлению")

> 10 ядер, Ubuntu Linux 18.04, Python 3.9.1

#### Параметры

```console
vera@vera$ lscpu
Architecture:        x86_64
CPU op-mode(s):      32-bit, 64-bit
CPU(s):              10
On-line CPU(s) list: 0-9
Thread(s) per core:  1
Core(s) per socket:  1
Socket(s):           10
NUMA node(s):        1
Vendor ID:           GenuineIntel
CPU family:          6
Model:               62
Model name:          Intel(R) Xeon(R) CPU E5-2630 v2 @ 2.60GHz
Stepping:            4
CPU MHz:             2599.998
BogoMIPS:            5199.99
Virtualization:      VT-x
Hypervisor vendor:   KVM
Virtualization type: full
L1d cache:           32K
L1i cache:           32K
L2 cache:            4096K
L3 cache:            16384K
```

#### Результаты

case | user time, s | kernel time, s | wall clock time, s | CPU, % | maximum resident set size, kbytes | comment | result 
-----|--------------|----------------| -------------------|------|-----------------------------------|---------|-------
[01-io-sequential.py](01-io-sequential.py) | 0.97 | 0.26 | **14.34** | 8% | 29 456 | долго, мало CPU используем, ждем большую часть времени | -
[02-io-threads.py](02-io-threads.py) | 1.03 | 0.37 | **1.75** | 80% | 56 612 | неплохо, но количество потоков лучше все-таки ограничить из-за возможного большого потребления ресурсов | +-
[03-io-processes.py](03-io-processes.py) | 1.15 | 0.67 | **1.41** | 129% | 27 916 | неплохо, но потоки дадут тот же результат при меньшем потреблении ресурсов | +- 
[04-io-thread_pool.py](04-io-thread_pool.py) (14 воркеров) | 1.04 | 0.28 | **2.02** | 65% | 50 700 | отличный вариант при грамотном подборе количества воркеров в пуле | ✅
[05-io-process_pool.py](05-io-process_pool.py) (10 воркеров) | 1.16 | 0.42 | **2.16** | 73% | 28 616 | неплохо, но пул потоков даст тот же результат при меньшем потреблении ресурсов | +-
[06-io-async.py](06-io-async.py) | 1.15 | 0.34 | **1.82** | 82% | 53 844 | отличный результат, сопоставимый с пулом потоков | ✅ 
[07-io-async-sequential.py](07-io-async-sequential.py) | 1.25 | 0.32 | **13.47** | 11% | 31 452 | даже хуже, чем последовательное выполнение из-за накладных расходов | -
[08-cpu-sequential.py](08-cpu-sequential.py) | 11.27 | 0.03 | **11.38** | 99% | 24 832 | очень долго | -
[09-cpu-threads.py](09-cpu-threads.py) | 13.28 | 0.32 | **14.29** | 95% | 25 656 | дольше последовательного выполнения из-за GIL + ненужные расходы на переключение контекста | -
[10-cpu-processes.py](10-cpu-processes.py) | 16.03 | 0.18 | **2.94** | 550% | 25 628 | неплохо, но количество потоков лучше все-таки ограничить из-за возможного большого потребления ресурсов | +-
[11-cpu-thread_pool.py](11-cpu-thread_pool.py) (14 воркеров) | 12.50 | 0.39 | **13.65** | 94% | 25 452 | дольше последовательного выполнения из-за GIL | -
[12-cpu-process_pool.py](12-cpu-process_pool.py) (10 воркеров) | 12.94 | 0.20 | **2.62** | 500% | 26 368 | отличный вариант при грамотном подборе количества воркеров в пуле, равного количеству ядер | ✅
[13-io+cpu-async.py](13-io+cpu-async.py) | 6.60 | 0.10 | **7.26** | 92% | 37 196 | общее время не маленькое, ioloop надолго блокируется | -
[14-io+cpu-async+thread_pool.py](14-io+cpu-async+thread_pool.py) (14 воркеров) | 6.36 | 0.23 | **6.72** | 98% | 37 480 | общее время тоже не маленькое, потоки из-за GIL не помогли | -
[15-io+cpu-async+process_pool.py](15-io+cpu-async+process_pool.py) (10 воркеров) | 6.57 | 0.31 | **1.93** | 355% | 38 188 | отличный результат! распараллелили и io- и cpu-bound задачи | ✅
[16-io+io_blocking-async.py](16-io+io_blocking-async.py) | 1.49 | 0.42 | **10.39** | 18% | 45 688 | общее время не маленькое, ioloop надолго блокируется | -
[17-io+io_blocking-async+thread_pool.py](17-io+io_blocking-async+thread_pool.py) (14 воркеров) | 1.39 | 0.40 | **2.41** | 74% | 59 872 | отличный результат! распараллелили и io- и cpu-bound задачи | ✅
[18-io+io_blocking-async+process_pool.py](18-io+io_blocking-async+process_pool.py) (10 воркеров) | 1.46 | 0.67 | **2.51** | 85% | 46 812 | результат тоже хороший (правда пул надо было сделать больше), но смысла нет, ресурсов потребует больше, чем вариант с потоками | +-

<a name="cpu2"></a>
### Тестовая машина #2 (2 ядра) [^](#index "к оглавлению")

> 2 ядра, MacOSX 10.14.6 Mojave, Python 3.9.1

#### Параметры

```console
Hardware Overview:

  Model Name:	MacBook Pro
  Processor Name:	Intel Core i7
  Processor Speed:	3,1 GHz
  Number of Processors:	1
  Total Number of Cores:	2
  L2 Cache (per Core):	256 KB
  L3 Cache:	4 MB
  Hyper-Threading Technology:	Enabled
```
> <sup>*</sup> `os.cpu_count()` в этой системе почему-то выводит 4

#### Результаты*

> <sup>*</sup> для mac os `time` не выводит %CPU, посчитала сама

case | user time, s | kernel time, s | wall clock time, s | CPU, % | maximum resident set size, kbytes | comment | result 
-----|--------------|----------------| -------------------|------|-----------------------------------|---------|-------
[01-io-sequential.py](01-io-sequential.py) | 0.97 | 0.11 | **17.22** | 6% | 33 005 | долго, мало CPU используем, ждем большую часть времени( | -
[02-io-threads.py](02-io-threads.py) | 0.95 | 0.14 | **2.59** | 42% | 55 779 | неплохо, но количество потоков лучше все-таки ограничить из-за возможного большого потребления ресурсов | +-
[03-io-processes.py](03-io-processes.py) | 11.86 | 1.79 | **5.60** | 244% | 30 831 | неплохо, но потоки дадут тот же результат при меньшем потреблении ресурсов | +- 
[04-io-thread_pool.py](04-io-thread_pool.py) (8 воркеров) | 0.93 | 0.12 | **3.10** | 34% | 39 378 | отличный вариант при грамотном подборе количества воркеров в пуле | ✅
[05-io-process_pool.py](05-io-process_pool.py) (4 воркера) | 2.54 | 0.36 | **5.46** | 53% | 33 116 | неплохо, но пул потоков даст тот же результат при меньшем потреблении ресурсов | +-
[06-io-async.py](06-io-async.py) | 1.46 | 0.24 | **3.16** | 54% | 61 505 | отличный результат, сопоставимый с пулом потоков | ✅ 
[07-io-async-sequential.py](07-io-async-sequential.py) | 1.75 | 0.28 | **17.98** | 11% | 37 490 | даже хуже, чем последовательное выполнение из-за накладных расходов | -
[08-cpu-sequential.py](08-cpu-sequential.py) | 11.23 | 0.07 | **11.55** | 97% | 24 408 | очень долго | -
[09-cpu-threads.py](09-cpu-threads.py) | 12.32 | 0.22 | **12.59** | 99% | 25 202 | дольше последовательного выполнения из-за GIL + ненужные расходы на переключение контекста | -
[10-cpu-processes.py](10-cpu-processes.py) | 29.72 | 1.17 | **9.13** | 338% | 25 382 | **выигрыш есть, но он не такой большой, как для 10-ядерной системы** | +-
[11-cpu-thread_pool.py](11-cpu-thread_pool.py) (8 воркеров) | 11.39 | 0.19 | **11.70** | 99% | 24 899 | дольше последовательного выполнения из-за GIL | -
[12-cpu-process_pool.py](12-cpu-process_pool.py) (4 воркера) | 24.13 | 0.31 | **7.68** | 318% | 25 780 | отличный вариант при грамотном подборе количества воркеров в пуле, равного количеству ядер, **результат хуже, чем для 10-ядерной системы** | ✅
[13-io+cpu-async.py](13-io+cpu-async.py) | 6.11 | 0.11 | **7.11** | 87% | 41 263 | общее время не маленькое, ioloop надолго блокируется | -
[14-io+cpu-async+thread_pool.py](14-io+cpu-async+thread_pool.py) (8 воркеров) | 6.14 | 0.15 | **6.8** | 93% | 41 984 | общее время тоже не маленькое, потоки из-за GIL не помогли | -
[15-io+cpu-async+process_pool.py](15-io+cpu-async+process_pool.py) (4 воркера) | 13.2 | 0.43 | **4.6** | 296% | 42 074 | распараллелили и io- и cpu-bound задачи, **результат есть, но он хуже, чем для 10-ядерной системы** | ✅
[16-io+io_blocking-async.py](16-io+io_blocking-async.py) | 1.38 | 0.20 | **12.26** | 12% | 53 547 | общее время не маленькое, ioloop надолго блокируется | -
[17-io+io_blocking-async+thread_pool.py](17-io+io_blocking-async+thread_pool.py) (8 воркеров) | 1.71 | 0.29 | **3.71** | 54% | 55 398 | отличный результат! распараллелили и io- и cpu-bound задачи | ✅
[18-io+io_blocking-async+process_pool.py](18-io+io_blocking-async+process_pool.py) (4 воркеров) | 3.41 | 0.61 | **5.31** | 55% | 53 899 | результат тоже хороший (правда пул надо было сделать больше), но смысла нет, ресурсов потребует больше, чем вариант с потоками | +-

<a name="cpu2"></a>
### Тестовая машина #3 (1 ядро) [^](#index "к оглавлению")

> 1 ядро, Ubuntu Linux 20.04, Python 3.8.2

#### Параметры

```console
vera@vera:~$ lscpu
Architecture:                    x86_64
CPU op-mode(s):                  32-bit, 64-bit
Address sizes:                   46 bits physical, 48 bits virtual
CPU(s):                          1
On-line CPU(s) list:             0
Thread(s) per core:              1
Core(s) per socket:              1
Socket(s):                       1
NUMA node(s):                    1
Vendor ID:                       GenuineIntel
CPU family:                      6
Model:                           13
Model name:                      QEMU Virtual CPU version 2.5+
Stepping:                        3
CPU MHz:                         2297.338
BogoMIPS:                        4594.67
Hypervisor vendor:               KVM
Virtualization type:             full
L1d cache:                       32 KiB
L1i cache:                       32 KiB
L2 cache:                        4 MiB
L3 cache:                        16 MiB
NUMA node0 CPU(s):               0
```

#### Результаты

case | user time, s | kernel time, s | wall clock time, s | CPU, % | maximum resident set size, kbytes | comment | result 
-----|--------------|----------------| -------------------|------|-----------------------------------|---------|-------
[01-io-sequential.py](01-io-sequential.py) | 1.01 | 0.10 | **15.05** | 7% | 33 488 | долго, мало CPU используем, ждем большую часть времени | -
[02-io-threads.py](02-io-threads.py) | 0.93 | 0.12 | **1.84** | 57% | 58 432 | неплохо, но количество потоков лучше все-таки ограничить из-за возможного большого потребления ресурсов | +-
[03-io-processes.py](03-io-processes.py) | 1.25 | 0.62 | **2.41** | 77% | 31 816 | неплохо, но потоки дадут тот же результат при меньшем потреблении ресурсов | +- 
[04-io-thread_pool.py](04-io-thread_pool.py) (5 воркеров) | 0.98 | 0.14 | **3.32** | 33% | 42 136 | отличный вариант при грамотном подборе количества воркеров в пуле | ✅
[05-io-process_pool.py](05-io-process_pool.py) (3 воркера) | 1.04 | 0.27 | **5.02** | 8% | 32 604 | неплохо, но пул потоков даст тот же результат при меньшем потреблении ресурсов | +-
[06-io-async.py](06-io-async.py) | 0.94 | 0.18 | **1.63** | 68% | 59 644 | отличный результат, сопоставимый с пулом потоков | ✅ 
[07-io-async-sequential.py](07-io-async-sequential.py) | 1.19 | 0.16 | **14.48** | 9% | 40 992 | даже хуже, чем последовательное выполнение из-за накладных расходов | -
[08-cpu-sequential.py](08-cpu-sequential.py) | 9.16 | 0.06 | **9.42** | 98% | 29 124 | **для одноядерной системы нет вариантов распараллеливания** | ✅
[09-cpu-threads.py](09-cpu-threads.py) | 9.85 | 0.16 | **10.29** | 97% | 30 032 | дольше последовательного выполнения из-за GIL + ненужные расходы на переключение контекста | -
[10-cpu-processes.py](10-cpu-processes.py) | 9.74 | 0.19 | **10.19** | 97% | 29 708 | **дольше последовательного выполнения из-за ненужных расходов на переключение контекста** | -
[11-cpu-thread_pool.py](11-cpu-thread_pool.py) (5 воркеров) | 9.53 | 0.12 | **9.79** | 98% | 29 888 | для одноядерной системы нет смысла использовать пул потоков (+ GIL) | -
[12-cpu-process_pool.py](12-cpu-process_pool.py) (3 воркера) | 9.89 | 0.13 | **9.80** | 98% | 30 600 | **для одноядерной системы нет смысла использовать пул процессов, получаем только дополнительные расходы** | -
[13-io+cpu-async.py](13-io+cpu-async.py) | 5.22 | 0.12 | **5.54** | 96% | 41 960 | общее время не маленькое, ioloop надолго блокируется | -
[14-io+cpu-async+thread_pool.py](14-io+cpu-async+thread_pool.py) (5 воркеров) | 5.22 | 0.13 | **5.57** | 96% | 42 076 | для одноядерной системы нет смысла использовать пул потоков (+ GIL) | -
[15-io+cpu-async+process_pool.py](15-io+cpu-async+process_pool.py) (3 воркера) | 5.49 | 0.20 | **5.94** | 95% | 42 712 | **процессы нам не помогли из-за одного ядра, но на будущий апгрейд железа оставляем его** | ✅
[16-io+io_blocking-async.py](16-io+io_blocking-async.py) | 1.25 | 0.09 | **10.15** | 13% | 54 024 | общее время не маленькое, ioloop надолго блокируется | -
[17-io+io_blocking-async+thread_pool.py](17-io+io_blocking-async+thread_pool.py) (5 воркеров) | 1.23 | 0.18 | **3.03** | 46% | 60 772 | отличный результат! распараллелили и io- и cpu-bound задачи | ✅
[18-io+io_blocking-async+process_pool.py](18-io+io_blocking-async+process_pool.py) (3 воркера) | 1.39 | 0.23 | **4.47** | 36% | 51 712 | результат тоже хороший (правда пул надо было сделать больше), но смысла нет, ресурсов потребует больше, чем вариант с потоками | +-

<a name="conclusion"></a>
## Выводы [^](#index "к оглавлению")

- выбор технологического решения зависит в первую очередь от задачи. io-bound - асинхронность или пул потоков, cpu - пул процессов
- GIL в питоне не позволяет эффективно использовать потоки для cpu-bound задач в отличие от других языков
- пул потоков вместо асинхронности стоит рассмотреть, когда время ожидания не очень большое и задач относительно немного
- еще один кейс использования пула потоков вместо асинхронности - отсутствие асинхронных библиотек под наши задачи (например, асинхронная работа с диском до сих пор не возможна)
- также, важны характеристики машин. Нет смысла использовать процессы или потоки для cpu-bound задач, если ядро всего лишь одно. Чем больше ядер - тем лучше
- количество воркеров в пуле процессов (используется для cpu-bound задач) рекомендуется делать равным количеству ядер, в пуле потоков (используется для io-bound задач) можно сделать больше в несколько раз
- для асинхронных приложений на многоядерных системах рекомендуется запустить несколько копий процесса (по количеству ядер) и делить между ними работу

<a name="resources"></a>
## Дополнительные материалы [^](#index "к оглавлению")
* [Асинхронное программирование. Event loop. Теория](https://github.com/vera-l/python-resources#async)
* [Многопоточность. GIL. Многопроцессные приложения](https://github.com/vera-l/python-resources#gil)
* [Потоки и их отличие отпроцессов на уровне OS. Лекция от mail.ru](https://www.youtube.com/watch?v=PbnnQknUvPw&list=PLrCZzMib1e9pOdLmE2qtMgL3QMEIrxyu7&index=7)
* [Убирая ГБИ (GIL) из Питона: Гилектомия (Д. Бизли) pycon 2016, русский перевод](https://www.youtube.com/watch?v=48l_HOtAqAI)
