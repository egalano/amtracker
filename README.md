amtracker
=========

Command-line interface to Amtrak train status and schedule data
Current destinations only include Los Angeles Union Station and Irvine, CA.
I will update this to add the remaining train destinations

Dependencies:
beautifulsoup
python-requests

Example Usage:

Shows the status of the 566 train from LAX to IRV on 2014-01-23
```
./amtracker.py -y 2014 -m 01 -d 23 --train 566 --origin lax --dest irv
```

Omitting the year and month sets it to the current year and current month
```
./amtracker.py -d 23 --origin lax --dest irv
```

Shows all relevant train information for today from LAX->IRV
```
./amtracker.py --origin lax --dest irv
```

Shows train 585's information for today from LAX->IRV
```
./amtracker.py --origin lax --dest irv --train 585
```
