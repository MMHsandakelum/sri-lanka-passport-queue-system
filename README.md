# sri-lanka-passport-queue-system
A serverless application built with AWS Lambda to manage and optimize queues at Sri Lanka's passport offices. This project is designed to reduce crowding, improve efficiency, and save time for citizens.

## System Architecture

The system consists of four AWS Lambda functions that handle different aspects of the queue management system:

### Components
- **Book Appointment**: Handles new appointment bookings and token generation
- **Get Queue Status**: Provides real-time queue status for a specific location
- **Advance Queue**: Manages queue progression and marks appointments as called
- **Notify User**: Sends email notifications to users when their turn is approaching
- **Python**: Runtime for all Lambdas

### Infrastructure
- AWS Lambda for serverless compute
- Amazon DynamoDB for data storage
- Amazon SES for email notifications

## API Endpoints

### API Base URL

- https://tjcr75txoa.execute-api.ap-south-1.amazonaws.com/prod

### Book Appointment
```json
POST /book-appointment
{
    "nic": "string",
    "name": "string",
    "email": "string",
    "location_id": "string",
    "date": "string",
    "time": "string"
}
```

### Get Queue Status
```json
GET /queue-status?location_id={location_id}&date={date}
```

### Advance Queue
```json
POST /advance
{
    "location_id": "string",
    "date": "string"
}
```

## Features

- Automated token generation for appointments
- Real-time queue status tracking
- Email notifications for upcoming appointments
- Queue management by location
- Token-based appointment system
- Automated status updates
- Fully serverless and scalable

## Data Structure

### Appointments Table
- appointment_id (Primary Key)
- nic
- name
- email
- location_id
- date
- time
- token
- status
- created_at

### Queue Status Table
- location_id (Primary Key)
- current_token

## Email Notifications
The system automatically notifies users when their token is about to be called (2 tokens ahead) via email using Amazon SES.


## Testing Instructions

1. Clone this repo:
   ```bash
   git clone https://github.com/MMHsandakelum/sri-lanka-passport-queue-system.git

2. Test API's are added to the git repository

  - sri-lanka-passport-queue-system.postman_collection.json

# IMPORTANT

    - This project uses Amazon SES to send email notifications when a customer's token is about to be called. Since my AWS account is currently in SES sandbox mode, I am only able to send emails to verified email addresses (including my own personal email).

    - In a production environment, this would be resolved by requesting SES production access, which would allow emails to be sent to any customer without prior verification.


