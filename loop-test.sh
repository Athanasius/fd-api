#!/bin/sh

while :;
do
	./get-profile.pl >/dev/null 2>&1
	case "$?" in
		255)
			/bin/echo -n "FAIL, "
			;;
		0)
			/bin/echo -n "SUCCESS, "
			;;
		*)
			echo "Huh? "
			;;
	esac
	#date
	sleep $1
done
