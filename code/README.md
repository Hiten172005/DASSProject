# Architecture and Components
rust_vtn_server: This is the server which is responsible to store pricing information and energy reports etc.
In deployment this server should be provided by an energy utility company. So its mostly a mock server.
However it can be used for actual deployment as well, and the utility could instead just use a VEN and connect to our VTN.

ven_code: this is the python ven server component. What this does is that it gets the prices and events from the VTN server, and serves them in a format meant for internal use. In the future after the protocol is devoloped further and the OpenADR team adds subscriptions, it will be able to receive events in realtime.

cero-smart-charging(optimizer): This is the component to which our client's software i.e Charge Management System (CMS) connects to. optimizer gets the prices from the python ven server and according to a price -> maxKiloWatts mapping it decides the maximum limits for charging and different points in the day. It has a default mapping for testing purposes, otherwise it receives the actual mapping in the post request body itself. It processes this inputs and creates a charging plan and sends it to CMS. The CMS transmits this to the charging station.

# Installation and first run

## Software dependencies:
1. Docker: latest
2. Java: Latest LTS JDK or (Java 17 JDK)
3. Maven: built,managed by intellij, if required you can use it directly as well
4. python: latest LTS
5. Intellij: (optional) for ease of use.

#### VTN server
1. Follow instructions in [rust_vtn_server/README.md](../rust_vtn_server/README.md) to get it running.
2. use the command in rust_vtn_server directory: `psql -U openadr -W openadr -h localhost openadr < fixtures/users.sql`. This is to load the admin creds used by ven_client
#### python ven server
3. Go to ven_code, install python requirements, do `py main.py` and done!, this inserts sample data everytime you run it automatically.
#### optimizer
4. go to cero-smart-charging. This process is more intuitive with an IDE (preferably intellij)
5. Run `mvn clean install`.
6. Find the jar (java executable package) in the target folder. Use the command `java -jar JARFILE_NAME.jar` to run it.
[Alternatively (requires maven)] Just run `mvn spring-boot:run` 

## How do I see it work?
You will need access to the client's demo website. Please contact and ask for that.<br>
1. Login
2. Navigate to Integrations page
3. Open smart charging
4. Paste the url of your optimizer
Note: This optimizer must be accessible on the public intranet. [Use VM or a simple tool like ngrok].
5. Now when you start a charging session, the session plans are automatically optimized.

(or)

1. Navigate to cero-smart-charging, open the postman folder.
2. Use postman or httpie software (both request files are in the `postman` folder) to send requests and see our software in action, play with the values.
3. To edit the price values you must use the OpenADR protocol and send prices to your VTN server, you could also tinker with our main.py and alter responses and add new price entries.


# Deploying
- Simply put the whole stack onto a EC2 or similar vm instance. create services for VEN client and optimizer. VTN server anyway runs on docker so a `docker compose up -d` is enough. (Configure docker to restart containers on machine reboot).
