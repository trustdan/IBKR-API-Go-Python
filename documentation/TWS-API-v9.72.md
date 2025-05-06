Introduction 

The TWS API is a simple yet powerful interface through which IB clients can automate their trading strategies, request market data and monitor your account balance and portfolio in real  time.

# Audience

Our TWS API components are aimed at experienced professional  developers willing to enhance the current TWS functionality.  Regrettably, Interactive Brokers cannot offer any programming  consulting. Before contacting our API support, please always refer to  our available documentation, sample applications and [Recorded Webinars](https://www.interactivebrokers.com/en/index.php?f=1350&t=recorded&p=1)

# How to use this guide

This guide reflects the very latest version of the TWS API -**9.72 and higher**- and constantly references the Java, VB, C#, C++ and Python **Testbed** sample projects to demonstrate the TWS API functionality. All code  snippets are extracted from these projects and we suggest all those  users new to the TWS API to get familiar with them in order to quickly  understand the fundamentals of our programming interface. The **Testbed** sample projects can be found within the **samples** folder of the TWS API's installation directory.

# Requirements

- • To obtain the TWS API source and sample code, download the [API Components](http://interactivebrokers.github.io/) (API version 9.73 or higher is required).
   • To make use of TWS API 9.73+, will require [TWS build](https://www.interactivebrokers.com/en/index.php?f=14099#tws-software) 952.x or higher.
   • A working knowledge of the programming language our **Testbed** sample projects are developed in.
   • Python version 3.1 or higher is required to interpret Python API client.
    

# Limitations

Our programming interface is designed to automate some of the  operations a user normally performs manually within the TWS Software  such as placing orders, monitoring your account balance and positions,  viewing an instrument's live data... etc. There is no logic within the  API other than to ensure the integrity of the exchanged messages. Most  validations and checks occur in the backend of TWS and our servers.  Because of this it is highly convenient to familiarize with the TWS  itself, in order to gain a better understanding on how our platform  works. Before spending precious development time troubleshooting on the  API side, it is recommended to first experiment with the TWS directly.

**Remember:** If a certain feature or operation is not available in the TWS, it will not be available on the API side either!

## Requests

The TWS is designed to accept up to **fifty** messages per second coming from the **client** side. Anything coming from the client application to the TWS counts as a message (i.e. requesting data, placing orders, requesting your  portfolio... etc.). This limitation is applied to **all** connected  clients in the sense were all connected client applications to the same  instance of TWS combined cannot exceed this number. On the other hand,  there are **no limits** on the amount of messages the TWS can send to the client application.

## Paper Trading

If your regular trading account has been approved and funded, you can use your Account Management page to open a [Paper Trading Account](https://www.interactivebrokers.com/en/software/am/am/manageaccount/papertradingaccount.htm) which lets you use the full range of trading facilities in a simulated  environment using real market conditions. Using a Paper Trading Account  will allow you not only to get familiar with the TWS API but also to  test your trading strategies without risking your capital. Note the  paper trading environment has inherent [limitations](https://www.interactivebrokers.com/en/software/am/am/manageaccount/paper_trading_limitations.htm).

## Intel® Decimal Floating-Point Math Library

This product includes Intel® Decimal Floating-Point Math Library (in  binary form) developed by the Intel Corporation under its license which  can be found [here](https://github.com/InteractiveBrokers/tws-api/blob/master/source/cppclient/client/lib/eula.txt).



...



Initial Setup 

The TWS API is an interface to IB's standalone trading applications, TWS and IB Gateway. These are both standalone,  Java-based trading applications which were designed to require the use  of a graphical user interface for secure user authentication. For that  reason "headless" operation of either application without a GUI is not  supported.

# The Trader Workstation

Our market maker-designed IB Trader Workstation (TWS) lets traders,  investors, and institutions trade stocks, options, futures, forex,  bonds, and funds on over 100 markets worldwide from a single account.  The TWS API is a programming interface to TWS, and as such, for an  application to connect to the API there must first be a running instance of TWS or IB Gateway. To use version 9.72+ of the API, it is necessary  to have TWS version 952 or higher.

# The IB Gateway

As an alternative to TWS for API users, IB also offers IB Gateway  (IBGW). From the perspective of an API application, IB Gateway and TWS  are identical; both represent a server to which an API client  application can open a socket connection after the user has  authenticated. With either application (TWS or IBGW), the user must  manually enter their username and password into a login window. For  security reasons, a headless session of TWS or IBGW without a GUI is not supported. From the user's perspective, IB Gateway may be advantageous  because it is a lighter application which consumes about 40% fewer  resources. IB Gateway is only provided in an 'offline' version, similar  to 'offline TWS', which does not update automatically. It is recommended to upgrade to a current version of IBGW on the website periodically  (note this does not require uninstalling the previous version of IBGW,  nor installing a different API version if not desired.)

Both TWS and IBGW were designed to be restarted daily. This is  necessary to perform functions such as re-downloading contract  definitions in cases where contracts have been changed or new contracts  have been added. Beginning in version 974+ both applications offer an  autorestart feature that allows the application to restart daily without user intervention. With this option enabled, TWS or IBGW can  potentially run from Sunday to Sunday without re-authenticating. After  the nightly server reset on Saturday night it will be necessary to again enter security credentials.

The advantages of TWS over IBGW is that it provides the end user with many tools (Risk Navigator, OptionTrader, BookTrader, etc) and a  graphical user interface which can be used to monitor an account or  place orders. For beginning API users, it is recommended to first become acquainted with TWS before using IBGW.

**For simplicity, this guide will mostly refer to the TWS although  the reader should understand that for the TWS API's purposes, TWS and IB Gateway are synonymous.**

# Logging into multiple applications

It is not possible to login to multiple trading applications  simultaneously with the same username. However, it is possible to create additional usernames for an account with can be used in different  trading applications simultaneously, as long as there is not more than a single trading application logged in with a given username at a time.  There are some additional cases in which it is also useful to create  additional usernames:

- If TWS or IBGW is logged in with a username that is used to login to Client Portal during that session, that application will not be able to automatically reconnect to the server after the next disconnection  (such as the server reset).
- A TWS or IBGW session logged into a paper trading account will not  to receive market data if it is sharing data from a live user which is  used to login to Client Portal.

If a different username is utilized to login to Client Portal in  either of these cases, then it will not affect the TWS/IBGW session.

[How to add additional usernames in Account Management](https://www.interactivebrokers.com/en/software/am3/am.htm#am/settings/addingusernamestoauser.htm)

- It is important to note that market data subscriptions are setup independently for each live username.

# Enable API connections

Before any client application can connect to the Trader Workstation,  the TWS needs to be configured to listen for incoming API connections on a very specific port. By default when TWS is first installed it will  not allow API connections. IBGW by contrast accepts socket-based API  connections by default. To enable API access in TWS, navigate to the  TWS' API settings at Edit -> Global Configuration -> API ->  Settings and make sure the "Enable ActiveX and Socket Clients" option is activated as shown below:

![enable_socket.png](https://interactivebrokers.github.io/tws-api/enable_socket.png)

Also important to mention is the "Socket port". By default a  production account TWS session will be set for socket port 7496, and a  paper account session will listen on socket port 7497. However these are just default values chosen because they are almost always available on  any computer. They can be changed to any open socket port, as long as  the socket ports specified in the API client and TWS settings match. If  there are multiple TWS sessions on one computer, the socket port is used to distinguish the TWS session. Since only one application can listen  on one port at a time you will need to assign different ports to each  running TWS.

**Important: when running paper and live TWS on the same computer,  make sure your client application is connecting to the right TWS!**

# Read Only API

The API Settings dialogue allows you to configure TWS to note accept  API orders with the "Read Only" setting. By default, "Read Only" is  enabled as an additional precautionary measure. Information about orders is not available to the API when read-only mode is enabled.

# Master Client ID

By default the "Master Client ID" field is unset. To specify that a certain client should *automatically* receive updates about all open orders, as well as commission reports  from orders placed from all clients, the client's ID should be set as  the Master Client ID in TWS or IBGW Global Configuration. The clientID  is specified from an API client application in the initial function call to [IBApi::EClientSocket::eConnect](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClientSocket.html#a315a7f7a34afc504d84c4f0ca462d924).

# Installing the API source

The API itself can be downloaded and installed from:

http://interactivebrokers.github.io/

Many third party applications already have their own version of the  API which is installed in the process of installing the third party  application. If using a third party product, it should first be verified if the API must be separately installed and what version of the API is  needed- many third party products are only compatible with a specific  API version.

Running the Windows version of the API installer creates a directory  "C:\\TWS API\" for the API source code in addition to automatically  copying two files into the Windows directory for the DDE and C++ APIs. ***It is important that the API installs to the \**C\**: drive\***, as otherwise API applications may not be able to find the associated  files. The Windows installer also copies compiled dynamic linked  libraries (DLL) of the ActiveX control TWSLib.dll, C# API CSharpAPI.dll, and C++ API TwsSocketClient.dll. Starting in API version **973.07**, running the API installer is designed to install an ActiveX control  TWSLib.dll, and TwsRTDServer control TwsRTDServer.dll which are  compatible with both 32 and 64 bit applications.

# Changing the installed API version

(On Windows Only)

If a different version of the ActiveX (**v9.71 or lower**) or C++  API is required than the one currently installed on the system, there  are additional steps required to uninstall the previous API version to  manually remove a file called "TwsSocketClient.dll":

1) Uninstall the API from the "Add/Remove Tool" in the Windows Control Panel as usual
2) Delete the C:\TWS API\ folder if any files are still remaining to prevent a version mismatch.
3) Locate the file "C:\Windows\SysWOW64\TwsSocketClient.dll". Delete this file.
4) Restart the computer before installing a different API version.



...



# EClientSocket and EWrapper Classes

Once the TWS is up and running and actively listening for incoming  connections we are ready to write our code. This brings us to the TWS  API's two major classes: the [IBApi.EWrapper](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html) interface and the [IBApi.EClientSocket](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClientSocket.html)

# Implementing the EWrapper Interface

The [IBApi.EWrapper](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html) interface is the mechanism through which the TWS delivers information  to the API client application. By implementing this interface the client application will be able to receive and handle the information coming  from the TWS. For further information on how to implement interfaces,  refer to your programming language's documentation.

- ​    1 class TestWrapper(wrapper.EWrapper):

# The EClientSocket Class

The class used to send messages to TWS is [IBApi.EClientSocket](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClientSocket.html). Unlike EWrapper, this class is not overriden as the provided functions  in EClientSocket are invoked to send messages to TWS. To use  EClientSocket, first it may be necessary to implement the [IBApi.EWrapper](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html) interface as part of its constructor parameters so that the application can handle all returned messages. Messages sent from TWS as a response  to function calls in [IBApi.EClientSocket](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClientSocket.html) require a EWrapper implementation so they can processed to meet the needs of the API client.

Another crucial element is the [IBApi.EReaderSignal](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EReaderSignal.html) object passed to theEClientSocket's constructor. With the exception of  Python, this object is used in APIs to signal a message is ready for  processing in the queue. (In Python the Queue class handles this task  directly). We will discuss this object in more detail in the [The EReader Thread](https://interactivebrokers.github.io/tws-api/connection.html#ereader) section.

- ​    1 class TestClient(EClient):

  ​    2    def __init__(self, wrapper):

  ​    3        EClient.__init__(self, wrapper)

   ... 

  ​    1 class TestApp(TestWrapper, TestClient):

  ​    2    def __init__(self):

  ​    3        TestWrapper.__init__(self)

  ​    4        TestClient.__init__(self, wrapper=self)

  **Note:**  The EReaderSignal class is not used for Python  API. The Python Queue module is used for inter-thread communication and  data exchange.



...



Connectivity 

A socket connection between the API client application and TWS is established with the [IBApi.EClientSocket.eConnect](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClientSocket.html#a315a7f7a34afc504d84c4f0ca462d924) function. TWS acts as a server to receive requests from the API  application (the client) and responds by taking appropriate actions. The first step is for the API client to initiate a connection to TWS on a  socket port where TWS is already listening. It is possible to have  multiple TWS instances running on the same computer if each is  configured with a different API socket port number. Also, each TWS  session can receive up to **32 different client applications** simultaneously. The **client ID** field specified in the API connection is used to distinguish different API clients.

# Establishing an API connection

Once our two main objects have been created, EWrapper and ESocketClient, the client application can connect via the [IBApi.EClientSocket](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClientSocket.html) object:

- ​    1        app.connect("127.0.0.1", args.port, clientId=0)

eConnect starts by requesting from the operating system that a TCP  socket be opened to the specified IP address and socket port. If the  socket cannot be opened, the operating system (not TWS) returns an error which is received by the API client as error code 502 to [IBApi.EWrapper.error](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#a7dfc221702ca65195609213c984729b8) (Note: since this error is not generated by TWS it is not captured in  TWS log files). Most commonly error 502 will indicate that TWS is not  running with the API enabled, or it is listening for connections on a  different socket port. If connecting across a network, the error can  also occur if there is a firewall or antivirus program blocking  connections, or if the router's IP address is not listed in the "Trusted IPs" in TWS.

After the socket has been opened, there must be an initial handshake  in which information is exchanged about the highest version supported by TWS and the API. This is important because API messages can have  different lengths and fields in different versions and it is necessary  to have a version number to interpret received messages correctly.

- For this reason it is important that the main EReader object is not  created until after a connection has been established. The initial  connection results in a negotiated common version between TWS and the  API client which will be needed by the EReader thread in interpreting  subsequent messages.

After the highest version number which can be used for communication  is established, TWS will return certain pieces of data that correspond  specifically to the logged-in TWS user's session. This includes (1) the  account number(s) accessible in this TWS session, (2) the next valid  order identifier (ID), and (3) the time of connection. In the most  common mode of operation the EClient.AsyncEConnect field is set to false and the initial handshake is taken to completion immediately after the  socket connection is established. TWS will then immediately provides the API client with this information.

- Important: The **IBApi.EWrapper.nextValidID** callback is  commonly used to indicate that the connection is completed and other  messages can be sent from the API client to TWS. There is the  possibility that function calls made prior to this time could be dropped by TWS.

There is an alternative, deprecated mode of connection used in  special cases in which the variable AsyncEconnect is set to true, and  the call to startAPI is only called from the connectAck() function. All  IB samples use the mode AsyncEconnect = False.

# The EReader Thread

API programs always have at least two threads of execution. One  thread is used for sending messages to TWS, and another thread is used  for reading returned messages. The second thread uses the API EReader  class to read from the socket and add messages to a queue. Everytime a  new message is added to the message queue, a notification flag is  triggered to let other threads now that there is a message waiting to be processed. In the two-thread design of an API program, the message  queue is also processed by the first thread. In a three-thread design,  an additional thread is created to perform this task. The thread  responsible for the message queue will decode messages and invoke the  appropriate functions in EWrapper. The two-threaded design is used in  the IB Python sample Program.py and the C++ sample TestCppClient, while  the 'Testbed' samples in the other languages use a three-threaded  design. Commonly in a Python asynchronous network application, the [asyncio module](https://docs.python.org/3/library/asyncio.ht) will be used to create a more sequential looking code design.

The class which has functionality for reading and parsing raw messages from TWS is the [IBApi.EReader](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EReader.html) class.

- In Python IB API, the code below is included in Client::connect(), so  the EReader thread is automatically started upon connection. There is 

  no need

   for user to start the reader. 

  ​    1        # You don't need to run this in your code!

  ​    2        self.reader = reader.EReader(self.conn, self.msg_queue)

  ​    3        self.reader.start()   # start thread

   Once the client is connected, a reader thread will be automatically  created to handle incoming messages and put the messages into a message  queue for further process. User 

  is required

   to trigger  Client::run() below, where the message queue is processed in an infinite loop and the EWrapper call-back functions are automatically triggered. 

  ​    1        app.run()

Now it is time to revisit the role of [IBApi.EReaderSignal](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EReaderSignal.html) initially introduced in [The EClientSocket Class](https://interactivebrokers.github.io/tws-api/client_wrapper.html#client_socket). As mentioned in the previous paragraph, after the EReader thread places a message in the queue, a notification is issued to make known that a  message is ready for processing. In the (C++, C#/.NET, Java) APIs, this  is done via the [IBApi.EReaderSignal](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EReaderSignal.html) object we initiated within the [IBApi.EWrapper](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html)'s implementer. In the Python API, it is handled automatically by the [Queue class](https://docs.python.org/3/library/queue.html).

The client application is now ready to work with the Trader  Workstation! At the completion of the connection, the API program will  start receiving events such as [IBApi.EWrapper.nextValidId](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#a09c07727efd297e438690ab42838d332) and [IBApi.EWrapper.managedAccounts](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#abd7e561f313bcc4c860074906199a46c). In TWS (*not IB Gateway*) if there is an active network connection, there will also immediately be callbacks to [IBApi::EWrapper::error](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#a7dfc221702ca65195609213c984729b8) with errorId as -1 and errorCode=*2104*,*2106*, errorMsg = "Market Data Server is ok" to indicate there is an active connection to the IB market data server. Callbacks to [IBApi::EWrapper::error](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#a7dfc221702ca65195609213c984729b8) with errorId as -1 do not represent true 'errors' but only  notifications that a connection has been made successfully to the IB  market data farms.

IB Gateway by contrast will not make connections to market data farms until a request is made by the IB client. Until this time the  connection indicator in the IB Gateway GUI will show a yellow color of  'inactive' rather than an 'active' green indication.

When initially making requests from an API application it is  important that the verifies that a response is received rather than  proceeding assuming that the network connection is ok and the  subscription request (portfolio updates, account information, etc) was  made successfully.

# Accepting an API connection from TWS

For security reasons, by default the API is not configured to  automatically accept connection requests from API applications. After a  connection attempt, a dialogue will appear in TWS asking the user to  manually confirm that a connection can be made:

![conn_prompt.png](https://interactivebrokers.github.io/tws-api/conn_prompt.png)

To prevent the TWS from asking the end user to accept the connection, it is possible to configure it to automatically accept the connection  from a trusted IP address and/or the local machine. This can easily be  done via the TWS API settings:

![tws_allow_connections.png](https://interactivebrokers.github.io/tws-api/tws_allow_connections.png)

**Note:** you have to make sure the connection has been fully  established before attempting to do any requests to the TWS. Failure to  do so will result in the TWS closing the connection. Typically this can  be done by waiting for a callback from an event and the end of the  initial connection handshake, such as [IBApi.EWrapper.nextValidId](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#a09c07727efd297e438690ab42838d332) or [IBApi.EWrapper.managedAccounts](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#abd7e561f313bcc4c860074906199a46c).

In rare cases in which IB Gateway or TWS has a momentarily delay in  establishing connecting to the IB servers, messages sent immediately  after receiving the nextValidId could be dropped and would need to be  resent. If the API client has not receive the expected callbacks from  issued requests, it should not proceed assumming the connection is ok.

# Broken API socket connection

If there is a problem with the socket connection between TWS and the  API client, for instance if TWS suddenly closes, this will trigger an  exception in the EReader thread which is reading from the socket. This  exception will also occur if an API client attempts to connect with a  client ID that is already in use.

The socket EOF is handled slightly differently in different API  languages. For instance in Java, it is caught and sent to the client  application to [IBApi::EWrapper::error](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#a7dfc221702ca65195609213c984729b8) with errorCode 507: "Bad Message". In C# it is caught and sent to [IBApi::EWrapper::error](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#a7dfc221702ca65195609213c984729b8) with errorCode -1. The client application needs to handle this error  message and use it to indicate that an exception has been thrown in the  socket connection. Associated functions such as [IBApi::EWrapper::connectionClosed](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#a9b0f099dc421e5a48ec290cab67a8ad1) and [IBApi::EClient::IsConnected](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#ab8e2702adca8f47228f9754f4963455d) functions are not called automatically by the API code but need to be handled at the API client-level*.

- This has been changed in API version 973.04



...



Financial Instruments (Contracts) 

# Overview

An [IBApi.Contract](https://interactivebrokers.github.io/tws-api/classIBApi_1_1Contract.html) object represents trading instruments such as a stocks, futures or options.

Every time a new request that requires a contract (i.e. market data,  order placing, etc.) is sent to TWS, the platform will try to match the  provided contract object with a single candidate. If there is more than  one contract matching the same description, TWS will return an error  notifying you there is an ambiguity. In these cases the TWS needs  further information to narrow down the list of contracts matching the  provided description to a single element.

The best way of finding a contract’s description is within the TWS  itself. Within the TWS, you can easily check a contract’s description  either by double clicking it or through the **Contract Info -> Description** menu, which you access by right-clicking a contract in TWS:

![contract_info_tws.png](https://interactivebrokers.github.io/tws-api/contract_info_tws.png)

The description will then appear:

![contract_description_tws_without_debug.png](https://interactivebrokers.github.io/tws-api/contract_description_tws_without_debug.png)

**Note:**  you can see the extended contract details by choosing **Contract Info -> Details**. This option will open a web page showing all available information on the contract.

Whenever a contract description is provided via the TWS API, the TWS  will try to match the given description to a single contract. This  mechanism allows for great flexibility since it gives the possibility to define the same contract in multiple ways.

The simplest way to define a contract is by providing its symbol,  security type, currency and exchange. The vast majority of stocks, CFDs, Indexes or FX pairs can be uniquely defined through these four  attributes. More complex contracts such as options and futures require  some extra information due to their nature. Below are several examples  for different types of instruments.

# ISLAND to NASDAQ API Compatibility

Upcoming *ISLAND* to *NASDAQ* naming change will make all of the *ISLAND* exchange definitions invalid.
 As a compatibility measure a new setting has been introduced in **TWS 10.16+**: *"Compatibility Mode: Send ISLAND for US Stocks trading on NASDAQ"*.
 This setting will enable all of the contract definitions with *ISLAND* exchange to be still acknowledged.
 It is **strongly recommended** to start implementing the *NASDAQ* exchange definition.

See also:

- [Requesting Contract Details](https://interactivebrokers.github.io/tws-api/contract_details.html)
- [Stock Contract Search](https://interactivebrokers.github.io/tws-api/matching_symbols.html)
- [Basic Contracts](https://interactivebrokers.github.io/tws-api/basic_contracts.html)
- [Spreads](https://interactivebrokers.github.io/tws-api/spread_contracts.html)


 ...



# Overview

Through the TWS API it is possible to define most orders already available within the TWS.

- [Available Orders](https://interactivebrokers.github.io/tws-api/available_orders.html)
- [Order Management](https://interactivebrokers.github.io/tws-api/order_management.html)
- [Minimum Price Increment](https://interactivebrokers.github.io/tws-api/minimum_increment.html)
- [Checking Margin Changes](https://interactivebrokers.github.io/tws-api/margin.html)
- [Trigger Methods](https://interactivebrokers.github.io/tws-api/trigger_method_limit.html)

## Changes in the date/time field

With the release of **TWS 10.17** and **TWS API 10.18** clients now can send date/time in different formats: 

- API allows UTC format "yyyymmdd-hh:mm:ss" in date/time fields.
   Example: *20220930-15:00:00* 
- API allows date/time field format with instrument's exchange timezone  (for all non-operator fields) and operator's time zone (for all fields).
   Example: *IBM 20220930-15:00:00 US/Eastern* 



...



Streaming Market Data 

It is possible to fetch different kinds market data from the TWS:

- [Top Market Data (Level I)](https://interactivebrokers.github.io/tws-api/top_data.html)
- [Market Depth (Level II)](https://interactivebrokers.github.io/tws-api/market_depth.html)
- [5 Second Real Time Bars](https://interactivebrokers.github.io/tws-api/realtime_bars.html)

# Live Market Data

In order to receive real time top-of-book, depth-of-book, or  historical market data from the API it is necessary have live market  data subscriptions for the requested instruments in TWS. The full list  of requirements for real time data:

(1) trading permissions for the specified instruments

(2) a funded account (except with forex and bonds), and

(3) market data subscriptions for the specified username

To subscribe to live market data:

Login to your [Account Management](https://gdcdyn.interactivebrokers.com/sso/Login), navigate to Manage Account -> Trade Configuration -> Market Data  and select the relevant packages and/or subscription you wish to  subscribe to based on the products you require.

One way to determine which market data subscriptions are required for a given security is to enter the contract into a TWS watchlist and the  right-click on the contract to select "Launch Market Data Subscription  Manager". This will launch a browser window to the market data  subscription page of a subscription covering the indicated instrument.

Alternatively, there is also a "Market Data Assistant" utility for determining market data subscriptions:

![am_market_data_subscription.png](https://interactivebrokers.github.io/tws-api/am_market_data_subscription.png)

Once you have selected the relevant packages, click on the "Continue" button and confirm you have made the right choices in the following  screen.

**Important:**  Market Data subscriptions are billable at the full month's rate and will not be pro-rated.

![am_subscription_confirm.png](https://interactivebrokers.github.io/tws-api/am_subscription_confirm.png)

# Sharing Market Data Subscriptions

Market data subscriptions are done at a **TWS user name** level,  not per account. This implies that live market data subscriptions need  to be purchased per every live TWS user. The only exception to this rule are paper trading users. To share the market data subscriptions simply  access your [Account Management](https://gdcdyn.interactivebrokers.com/sso/Login) and navigate to Manage Account -> Settings -> Paper Trading where you will be presented to the screen below. It will take up to 24 hours  until the market data sharing takes effect.

![am_md_sharing.png](https://interactivebrokers.github.io/tws-api/am_md_sharing.png)

**Important:** since your paper trading market data permissions  are bound to your live one, you can only obtain live market data on your paper trading user if;

- You have shared the market data subscriptions accordingly as described above.
- You are NOT logged in with your live user name at the same time on a **different** computer.

# Market Data Lines

Whenever a user requests an instrument's real time (top-of-book)  market data either from within the TWS or through the TWS API, the user  is making use of a market data line. Market data lines therefore  represent the **active** market data requests a user has.

**Example:**  To clarify this concept further, let us assume a user has a maxTicker Limit of **ten** market data lines and is already observing the real time data of say **five** stocks within the TWS itself. When the user connects his TWS API client application to the TWS, he then requests the real time market data for  another **different five** instruments. At a later point while all 10 requests are still active, the user tries to subscribe to the live real time market data of an eleventh product. Since the user is already  making use of ten market data lines (five in the TWS and another five in his client application), the TWS will respond with an error message  telling the client application it has reached the maximum number of  simultaneous requests. In order to request the market data of the  eleventh product, the user will have to cancel at least one of the  currently active subscriptions (either within TWS or from his client  program.)

By default, every user has a maxTicker Limit of 100 market data lines and as such can obtain the real time market data of up to 100  instruments **simultaneously**. This limit however can be further  extended either through the purchase of quote booster packs or by  increasing the equity and/or commissions of the user's account. For  further details on how to increment the number of market data lines or  how is your market data lines' entitlement calculated, please refer to  our website's "Market Data Display" section within the [Research, News and Market Data](https://www.interactivebrokers.com/en/index.php?f=14193) page.

**Note:** It is important to understand the concept of market data lines since it has an impact not only on the live real time requests  but also for requesting market depth and real time bars.

# Quotes in shares

Previously, US stock size quotes were displayed in round lots (of 100 shares). 
 Effective with TWS release 985 and above, the bid, ask, and last size quotes are displayed in shares instead of lots. 
 API users have the option to configure the TWS API to work in  compatibility mode for older programs, but we recommend migrating to  "quotes in shares" at your earliest convenience. 
 To use compatibility mode, from the Global Configuration > API >  Settings page, check "Bypass US Stocks market data in shares warning for API orders."



...



Historical Market Data 

Receiving historical data from the API has the same market data subscription requirement as receiving streaming  top-of-book live data [Live Market Data](https://interactivebrokers.github.io/tws-api/market_data.html#market_subscriptions). The API historical data functionality pulls certain types of data from  TWS charts or the historical Time&Sales Window. So if data is not  available for a specific instrument, data type, or period within a TWS  chart it will also not be available from the API. Unlike TWS, which can  create 'delayed charts' for most instruments without any market data  subscriptions that have data up until 10-15 minutes prior to the current moment; the API always requires Level 1 streaming real time data to  return historical data.

- In general, a **smart-routed** historical data requests will require subscriptions to **all exchanges** on which a instrument trades.
- For instance, a historical data request for a pink sheet (OTC) stock which trades on ARCAEDGE will require the subscription "OTC Global  Equities" or "Global OTC Equities and OTC Markets" for ARCAEDGE in  addition to the regular subscription (e.g. "OTC Markets").
- When retrieving historical data from the TWS, be aware of the [Historical Data Limitations](https://interactivebrokers.github.io/tws-api/historical_limitations.html).

## Types of Historical Data Available

- [Historical Bar Data](https://interactivebrokers.github.io/tws-api/historical_bars.html)
- [Histograms](https://interactivebrokers.github.io/tws-api/histograms.html)
- [Historical Time and Sales Data](https://interactivebrokers.github.io/tws-api/historical_time_and_sales.html)

Finding earliest date historical data is available for an instrument

- [Finding Earliest Data Point](https://interactivebrokers.github.io/tws-api/head_timestamp.html)

Note about Interactive Brokers' historical data:

- Historical data at IB is filtered for trade types which occur away  from the NBBO such as combo legs, block trades, and derivative trades.  For that reason the daily volume from the (unfiltered) real time data  functionality will generally be larger than the (filtered) historical  volume reported by historical data functionality. Also, differences are  expected in other fields such as the VWAP between the real time and  historical data feeds.

## Changes in the date/time field

With the release of **TWS 10.17** and **TWS API 10.18** clients now can send date/time in different formats: 

- API allows UTC format "yyyymmdd-hh:mm:ss" in date/time fields.
   Example: *20220930-15:00:00* 
- API allows date/time field format with instrument's exchange timezone  (for all non-operator fields) and operator's time zone (for all fields).
   Example: *IBM 20220930-15:00:00 US/Eastern* 



...



The TWS offers a comprehensive overview of  your account and portfolio through its Account and Portfolio windows.  This information can be obtained via the TWS API through three different kind of requests/operations:

- [Managed Accounts](https://interactivebrokers.github.io/tws-api/managed_accounts.html)
- [Family Codes](https://interactivebrokers.github.io/tws-api/family_codes.html)
- [Account Updates](https://interactivebrokers.github.io/tws-api/account_updates.html)
- [Account Summary](https://interactivebrokers.github.io/tws-api/account_summary.html)
- [Positions](https://interactivebrokers.github.io/tws-api/positions.html)
- [Profit And Loss (P&L)](https://interactivebrokers.github.io/tws-api/pnl.html)
- [White Branding User Info](https://interactivebrokers.github.io/tws-api/wb_user_info.html) 



...



Options 

# Option Chains

The option chain for a given security can be returned using the  function reqContractDetails. If an option contract is incompletely  defined (for instance with the strike undefined) and used as an argument to [IBApi::EClient::reqContractDetails](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#ade440c6db838b548594981d800ea5ca9), a list of all matching option contracts will be returned.

The example below shows an "incomplete" option [IBApi.Contract](https://interactivebrokers.github.io/tws-api/classIBApi_1_1Contract.html) with no last trading day, strike nor multiplier defined. In most cases  using such a contract would result into a contract ambiguity error since there are lots of instruments matching the same description. [IBApi.EClient.reqContractDetails](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#ade440c6db838b548594981d800ea5ca9) will instead use it to obtain the whole option chain from the TWS.

- ​    1        contract = Contract()

  ​    2        contract.symbol = "FISV"

  ​    3        contract.secType = "OPT"

  ​    4        contract.exchange = "SMART"

  ​    5        contract.currency = "USD"

   ... 

  ​    1        self.reqContractDetails(210, ContractSamples.OptionForQuery())

  ​    2        self.reqContractDetails(211, ContractSamples.EurGbpFx())

  ​    3        self.reqContractDetails(212, ContractSamples.Bond())

  ​    4        self.reqContractDetails(213, ContractSamples.FuturesOnOptions())

  ​    5        self.reqContractDetails(214, ContractSamples.SimpleFuture())

  ​    6        self.reqContractDetails(215, ContractSamples.USStockAtSmart())

  ​    7        self.reqContractDetails(216, ContractSamples.CryptoContract())

  ​    8        self.reqContractDetails(217, ContractSamples.ByIssuerId())

  ​    9        self.reqContractDetails(219, ContractSamples.FundContract())

One limitation of this technique is that the return of option chains  will be throttled and take a longer time the more ambiguous the contract definition. Starting in version 9.72 of the API, a new function [IBApi::EClient::reqSecDefOptParams](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#adb17b291044d2f8dcca5169b2c6fd690) is introduced that does not have the throttling limitation.

- It is not recommended to use reqContractDetails to receive complete  option chains on an underlying, e.g. all combinations of  strikes/rights/expiries.
- For very large option chains returned from reqContractDetails,  unchecking the setting in TWS Global Configuration at API -> Settings -> "Expose entire trading schedule to the API" will decrease the  amount of data returned per option and help to return the contract list  more quickly.

- ​    1        self.reqSecDefOptParams(0, "IBM", "", "STK", 8314)

   ... 

  ​    1    def securityDefinitionOptionParameter(self, reqId: int, exchange: str,

  ​    2                                          underlyingConId: int, tradingClass: str, multiplier: str,

  ​    3                                          expirations: SetOfString, strikes: SetOfFloat):

  ​    4        super().securityDefinitionOptionParameter(reqId, exchange,

  ​    5                                                  underlyingConId, tradingClass, multiplier, expirations, strikes)

  ​    6        print("SecurityDefinitionOptionParameter.",

  ​    7              "ReqId:", reqId, "Exchange:", exchange, "Underlying conId:", intMaxString(underlyingConId), "TradingClass:", tradingClass, "Multiplier:", multiplier,

  ​    8              "Expirations:", expirations, "Strikes:", str(strikes))

[IBApi::EClient::reqSecDefOptParams](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#adb17b291044d2f8dcca5169b2c6fd690) returns a list of expiries and a list of strike prices. In some cases  it is possible there are combinations of strike and expiry that would  not give a valid option contract.

The API can return the greek values in real time for options, as well as calculate the implied volatility given a hypothetical price or  calculate the hypothetical price given an implied volatility.

- [Option Greeks](https://interactivebrokers.github.io/tws-api/option_computations.html)

# Exercising options

Options are exercised or lapsed from the API with the function [IBApi.EClient.exerciseOptions](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#a3d26e16bd4436a64f422c7e5c813ff16)

- Option exercise will appear with order status side = "BUY" and limit price of 0, but only at the time the request is made
- Option exercise can be distinguished by price = 0

- ​    1        self.exerciseOptions(5003, ContractSamples.OptionWithTradingClass(), 1,

  ​    2                             1, self.account, 1, "20231018-12:00:00")



...



Fundamental Data 

Starting with *TWS v985+* and after *API v985+*, **Fundamental** data from the **Wall Street Horizon Event Calendar** can be accessed via the TWS API through the functions [IBApi.EClient.reqWshMetaData](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#a66b482661e36604c43c4a7087bd7840f) and [IBApi.EClient.reqWshEventData](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#ac3dcd47d72844657c71e9de109eb15d0). It is necessary to have the Wall Street Horizon Enchilada Pro research subscription activated first in [Account Management](http://interactivebrokers.github.io/tws-api/market_data.html#market_subscriptions).
 WSH provides IBKR with corporate event datasets, including earnings  dates, dividend dates, options expiration dates, splits, spinoffs and a  wide variety of investor-related conferences.

The function [IBApi.EClient.reqWshMetaData](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#a66b482661e36604c43c4a7087bd7840f) is used to request metadata describing calendar events.

- ​    1        self.reqWshMetaData(1100)

The metadata is then received via the callback [IBApi.EWrapper.wshMetaData](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#ac9de56b7a92ccc5833a44d09f1f5894c)

- ​    1    def wshMetaData(self, reqId: int, dataJson: str):

  ​    2        super().wshMetaData(reqId, dataJson)

  ​    3        print("WshMetaData.", "ReqId:", reqId, "Data JSON:", dataJson)

Pending metadata requests can be canceled with the function [IBApi.EClient.cancelWshMetaData](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#aba0873c63be720f0c7349931df58376b) 

The function [IBApi.EClient.reqWshEventData](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#ac3dcd47d72844657c71e9de109eb15d0) is used to request the calendar events. *Note:* Prior to sending this message, it is expected that the API client request metadata via [IBApi.EClient.reqWshMetaData](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#a66b482661e36604c43c4a7087bd7840f), else an error may be reported.

- ​    1        wshEventData1 = WshEventData()

  ​    2        wshEventData1.conId = 8314

  ​    3        wshEventData1.startDate = "20220511"

  ​    4        wshEventData1.totalLimit = 5

  ​    5        self.reqWshEventData(1101, wshEventData1)

As seen above, currently the event data can only be filtered by  conId. At a later point, filter parameters may be added for account,  datePeriod, wholeMonthEvents, etc.

The event data is then received via the callback [IBApi.EWrapper.wshEventData](https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#ab4c0efad8874acb622f96b8d07f18c8e)

- ​    1    def wshEventData(self, reqId: int, dataJson: str):

  ​    2        super().wshEventData(reqId, dataJson)

  ​    3        print("WshEventData.", "ReqId:", reqId, "Data JSON:", dataJson)

Pending event data requests can be canceled with the function [IBApi.EClient.cancelWshEventData](https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#a5317aac7fb42545d519b46709b70c805)

Also note that TWS will not support multiple concurrent requests.  Previous request should succeed, fail, or be cancelled by client before  next one. TWS will reject such requests with text "Duplicate WSH  meta-data request" or "Duplicate WSH event request".

In **TWS API 10.15+** Wall Street Horizon Event Calendar queries and filters have been added. For guidelines and more information please visit [Wall Street Horizon Corporate Event filters](https://interactivebrokers.github.io/tws-api/wshe_filters.html) page.