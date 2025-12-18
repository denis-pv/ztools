## check_bridges.py

 - проверяет мосты из файла bridges.txt
 - рабочие складывает в actual_bridges.txt
 - не рабочие в dead_bridges.txt


## check_bridges_rc.py - вариант для ubuntu server
 - проверяет доступность мостов из /etc/tor/torrc
 - рабочие складывает в файл bridges_works.torrc

## обновить под линукс и запустить одной коммандой
	git stash && git pull && chmod 777 *.py && ./check_bridges_rc.py