![Figure](API Documentation Boreal 26-07-23-01.assets/page-1-img-0.png)

# API Documentation example Boreal

# Version 26-07-23-01

Access to the API is provided to service accounts. The URL and credentials are

provided on request. API access requires a REALM subscription.

## Boreal tag traits example

Tag traits (tagID) are the unique identifier for a channel throughout the Brightlayer

system. Therefore, the API works with tagIDs. The tagID for each channel can be

retrieved from the ontology file. Examples:

- 
Name: "totalwater_in", tagID 10462371

- 
Name: "totalwater_pro", tagID 10462372

## URL

The following URL (prefix) needs to be used to access the API on the EMEA Prod

system:

**[https://portal.machinery-monitoring.com**](https://portal.machinery-monitoring.com**)

1

![Figure](API Documentation Boreal 26-07-23-01.assets/page-2-img-0.png)

### Real-time API

**POST <prefix>/api/v1/dashboard/devices/{deviceId}/realtime**

This API will return the real-time data for a device. Only realtime data will be returned by

this API.

**Non-Normative Request Example**

Request query parameter:

- 
```
deviceId : 9e153413-fcf1-2b11-0800-a887d221b600 
```

Request body:

{

"tagId": "string"

}

Request body example:

{

"tagId": "10419813"

}

**Non-Normative Response Example on Success**

Response status code: 200

Response body:

{

"v": {

"unit": "",

"value": "true"

},

"dt": "2025-07-17T08:00:44Z"

}

Response description:

- 
v - collection of the values returned from real-time query result:

o

unit - unit of the trait.

o

value - current value of datapoint/trait.

- 
dt - timestamp.

2

![Figure](API Documentation Boreal 26-07-23-01.assets/page-3-img-0.png)

## Time-series / Trends API

**POST <prefix>/api/v1/dashboard/devices/timeseries**

This will return the time-series data for a list of devices.

**Non-Normative Request Example**

Request body:

{

"devices": [

{

"deviceId": "String",

"tagTrait": "String"

}

],

"startDateTime": "DateTime (UTC)",

"endDateTime": "DateTime (UTC)"

}

Example:

{

- devices":[
{

"deviceId": "967071e5-83e1-2b11-0800-8c08ae746b00",

"tagTrait": "10361718"

}

],

- startDateTime": "2025-07-15T00:00:00Z",
- endDateTime": null
}

Request properties description:

- 
devices (required) - collection of the devices and tag/trait pairs for which the

telemetry is queried:

o

deviceId (required) - id of the device.

o

tagTrait (required) - the tag trait for the device.

- 
startDateTime (required) - start time of the time range for time series query.

- 
endDateTime (optional) - end time of the time range for time series query.

3

![Figure](API Documentation Boreal 26-07-23-01.assets/page-4-img-0.png)

**Non-Normative Response Example on Success**

Response status code: 200

Response body:

{

"timeSeries": [

{

"tagTrait": "10361718",

"deviceId": "9e153413-fcf1-2b11-0800-a887d221b600",

"results": {

"values": [

{

"v": {

"unit": "kWh",

"value": "123"

},

"dt": "2025-04-15T09:16:28Z"

}

]

}

},

{

"tagTrait": "10415480",

"deviceId": "9e153413-fcf1-2b11-0800-a887d221b600",

"results": {

"values": [

{

"v": {

"unit": "kWh",

"value": "456"

},

"dt": "2025-04-15T09:16:28Z"

}

]

}

}

]

}

Response description:

- 
the response is a collection of the timeseries query result. Every element of that

collection is differed by deviceId, tag.

- 
deviceId - GUID of the device.

- 
results - collection of the timeseries query results.

o

trait - trends data trait .

o

values - collection of timeseries values.

- 
v - value of the trait.

- 
dt - timestamp.

4

![Figure](API Documentation Boreal 26-07-23-01.assets/page-5-img-0.png)

## Command API

## Remark: Currently no control channels are defined in

## the water_filtration ontology.

**POST <prefix>/api/v1/dashboard/devices/{deviceId}/command**

Update the device command sent from the cloud to the device. Device commands can

only be sent to channels that are of the type “control”. The range of data, that can be

sent to the device, is defined in the ontology.

**Non-Normative Request Example**

Request query parameter:

- 
deviceId : ba8ef5d8-b33d-42fd-85d0-416fa73345a0

Request body:

[{

"tagId": "String",  // tag id for control channel

"value" : "string" // data range needs to be defined in the ontology

}]

Example:

1. Control command one
[{

"tagId": "10420585",

"value" : "1"

}]

2. Control command two
[{

"tagId": "10420586",

"value" : "1"

}]

**Non-Normative Response Example**

Response status code: 201 if value is set successfully.

Response status code: 404 if channel not found.

5

![Figure](API Documentation Boreal 26-07-23-01.assets/page-6-img-0.png)

- 
tagIds(required) - collection of the tag ids for which data should be queried:

o

outletStatus(required) - tag id for the outlet status channel.

o

energyconsumptionactual(required) - tag id for the energy consumption actual

channel.

**Non-Normative Response Example on Success**

Response status code: 200

Response body:

{

"v": {

"unit": "kWh",

"value": "0.4"

},

"dt": "2025-07-17T10:37:35Z"

}

Response description:

- 
v - collection of the values returned from real-time query result:

o

unit - unit of the trait.

o

value - current value of datapoint/trait.

- 
dt - timestamp.

6

![Figure](API Documentation Boreal 26-07-23-01.assets/page-7-img-0.png)

## Devices API

**GET <prefix>/api/v1/dashboard/organization/{organizationId}/devices**

This API is designed for retrieving the device id and name mapping of devices that are

present within an organization.

**Non-Normative Request Example**

Request query parameter:

- 
organizationId : 723af19b-95d6-43e0-b629-a18d1efe9225

**Non-Normative Response Example on Success**

Response status code: 200

Response body:

{

"id": "723af19b-95d6-43e0-b629-a18d1efe9225",

"devices": [

{

"id": "0639aba5-09a5-4671-a119-d6b684e81736",

"name": "P0001-S0001-01"

},

{

"id": "579b3195-fbd4-4cee-b857-99109445b9bb",

"name": "P0002-S0001-01"

},

{

"id": "e99b2311-a69a-40f0-92b0-5065be9164de",

"name": "P0003-S0001-01"

}

]

}

Response description:

- 
id    - organization id.

- 
devices – collection of devices:

o id – device id.

o name – device name.

7

![Figure](API Documentation Boreal 26-07-23-01.assets/page-8-img-0.png)

## API to generate the token:

**POST <prefix>/api/v1/auth/serviceaccount/token**

**Non-Normative Request Example:**

Request body:

{

- serviceAccountId": "string",
- secret": "string"
}

**Non-Normative Response Example on Success**

Response status code: 200

Response body:

{

- token":
- eyJraWQiOiJKaHQtQjRpWFpmRHVBUkF1Ykdra1NfM1o1SktkOVp3Q0pwM3laWlha"
}

8
