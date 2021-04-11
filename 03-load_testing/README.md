# Нагрузочное тестирование

<a name="index"></a>
* <a href="#theory">Теория</a>
  * <a href="#terms">Термины</a>
  * <a href="#load-testing-tools">load-testing тулзы</a>
    * <a href="#ab">ab</a>
    * <a href="#wrk">wrk</a>
    * <a href="#vegeta">vegeta</a>
* <a href="#test-apps">Тестовые приложения</a>
  * <a href="#tornado">tornado</a>
  * <a href="#aiohttp">aiohttp</a>
  * <a href="#sanic">sanic</a>
  * <a href="#flask">flask</a>
  * <a href="#bottle">bottle</a>
* <a href="#cases">Кейсы</a>
  * <a href="#framework">Выбор фреймворка под наши задачи</a>
  * <a href="#solution">Проверка своей гипотезы на выбор технологического решения</a>
  * <a href="#async-work">Как работает асинхронное приложение и что для него плохо</a>
  * <a href="#flamegraph">Исследование работы приложения под нагрузкой</a>
  * <a href="#memory_leak">Воспроизведение ситуации на проде</a>
* <a href="#conclusion">Выводы</a>
* <a href="#resources">Дополнительные материалы</a>

<a name="theory"></a>
## Теория [^](#index "к оглавлению")

<a name="terms"></a>
### Термины

<a name="load-testing-tools"></a>
### load-testing тулзы

<a name="ab"></a>
#### ab

Установка:

```console
apt install apache2-utils
```

Использование:

```console
vera@~/dev/frontik$ ab -n 100 -c 100 http://0.0.0.0:8000/
This is ApacheBench, Version 2.3 <$Revision: 1826891 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 0.0.0.0 (be patient).....done


Server Software:        
Server Hostname:        0.0.0.0
Server Port:            8000

Document Path:          /
Document Length:        17 bytes

Concurrency Level:      100
Time taken for tests:   0.223 seconds
Complete requests:      100
Failed requests:        0
Total transferred:      10700 bytes
HTML transferred:       1700 bytes
Requests per second:    447.60 [#/sec] (mean)
Time per request:       223.416 [ms] (mean)
Time per request:       2.234 [ms] (mean, across all concurrent requests)
Transfer rate:          46.77 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    5   1.4      5       6
Processing:     8  197  28.1    213     215
Waiting:        2  174  43.0    198     211
Total:          8  202  27.8    216     220

Percentage of the requests served within a certain time (ms)
  50%    216
  66%    217
  75%    218
  80%    218
  90%    219
  95%    220
  98%    220
  99%    220
 100%    220 (longest request)
```

<a name="wrk"></a>
#### wrk

https://github.com/wg/wrk

```console
vera@~vera$ wrk -c100 -t1 -d15s http://0.0.0.0:8000
Running 15s test @ http://0.0.0.0:8000
  1 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   141.66ms   49.47ms 286.28ms   61.39%
    Req/Sec   718.79    221.37     1.42k    73.33%
  10597 requests in 15.09s, 1.28MB read
Requests/sec:    702.09
Transfer/sec:     87.08KB
```

<a name="vegeta"></a>
#### vegeta

https://github.com/wg/wrk

```console
wrk -c100 -t1 -d15s http://0.0.0.0:8080
```

<a name="test-apps"></a>
## Тестовые приложения [^](#index "к оглавлению")


<a name="cases"></a>
## Кейсы [^](#index "к оглавлению")



<a name="conclusion"></a>
## Выводы [^](#index "к оглавлению")

<a name="resources"></a>
## Дополнительные материалы [^](#index "к оглавлению")

* [Нагрузочное тестирование web-сервера при помощи ab](http://ashep.org/2011/nagruzochnoe-testirovanie-web-servera/)
* [Load Testing with Vegeta](https://www.scaleway.com/en/docs/vegeta-load-testing/)
