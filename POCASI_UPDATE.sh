curl "https://api.openweathermap.org/data/2.5/onecall?lat=50.77&lon=15.06&lang=cz&appid=______OPENWEATHER API_______b&units=metric&exclude=minutely,hourly" --connect-timeout 5 | jq . > /home/tmpfs/pocasi-onecall_new.json
returncode=$?
if [ "$returncode" -eq "0" ]
then
	echo "Curl stáhl soubor s počasím."
	mv /home/tmpfs/pocasi-onecall_new.json /home/tmpfs/pocasi-onecall.json
	echo "Soubor s počasím přesunut pevného bodu."
else
	echo "!! Curl nestáhl soubor s počasím - není připojení nebo nefunguje openweathermap.org."
fi
#iconv -f utf8 -t ascii//TRANSLIT pocasi-onecall.json > pocasi-onecall-bd.json
