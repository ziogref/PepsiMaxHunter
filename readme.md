PepsiMaxHunter uses the pre-filled links in lines 4-9.
the Program then accesses the links and pulls the prices and pack sizes from the JSON data then performs math to get the price per can
It then sorts the results by price per can
It then pushes the result via Pushover

Lines 145 and 146 need to be edited with your pushover account info.

This is currently optimised for Pepsi Max only and appears to have issues with other canned drinks. I am going to be working on changing this to universal support for all multi-pack can drink products.

Pushover is a free Push notification software (not owned by me) that you can call an API to send push notifications to other devices, like iPhone and Android phones.
The mobile app does have a one-time purchase price.
Pushover.net
