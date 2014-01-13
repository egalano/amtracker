amtracker
=========

Command-line interface to Amtrak train statua and schedule data
Current destinations only include Los Angeles Union Station and Irvine, CA.
I will update this to add the remaining train destinations

Dependencies:
beautifulsoup
python-requests

Example Usage:

```
./amtracker.py -y 2014 -m 01 -d 23 --train 566 --origin lax --dest irv
```

# Omitting the month a day sets it to the current month and current day
```
./amtracker.py -d 23 --train 566 --origin lax --dest irv
```

# Shows all relevant train information for today from LAX->IRV
```
./amtracker.py --origin lax --dest irv
```
