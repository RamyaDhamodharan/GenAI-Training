# GenAI-Training

# Week 1 - Day 1 API Practical

## 1. Open-Meteo Weather API

### Method
GET

### Endpoint
https://api.open-meteo.com/v1/forecast

### Authentication
None

### Headers
No required authentication headers.

### Query Parameters
- latitude
- longitude
- hourly
- Currentweather

### Response
JSON weather forecast data.


## 2. Nager.Date Public Holidays API

### Method

GET


### Endpoint

https://date.nager.at/api/v4/Holidays/AT/2026

### Authentication

None

### Headers

No required authentication headers.

### Query Parameters

No query parameters.

### Country code and year are provided directly in the URL path:

AT → Country code (Austria) |    IN → Country code (INDIA)
2026 → Year

### Response
JSON list containing public holiday information.

Each holiday contains details such as:

date
name
countryCode       (optional)
nationalHoliday   (optional)
subdivisionCodes  (optional)
holidayTypes      (optional)


## 3. Frankfurter Exchange Rate API

### Method

GET

### Endpoint

[https://api.frankfurter.dev/v1/latest](https://api.frankfurter.dev/v1/latest)

### Authentication

None

### Headers

No required authentication headers.

### Query Parameters

base
symbols

### Response

JSON exchange-rate data containing:

amount
base
date
rates
