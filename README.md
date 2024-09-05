# Elastic Face Recognition Application using IaaS

This project implements a scalable face recognition application using AWS IaaS resources. The application is designed with a multi-tier architecture, consisting of a Web Tier, App Tier, and Data Tier, with autoscaling capabilities to handle varying loads.

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Components](#components)
  - [Web Tier](#web-tier)
  - [App Tier](#app-tier)
  - [Data Tier](#data-tier)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Testing](#testing)
- [Autoscaling Algorithm](#autoscaling-algorithm)
- [License](#license)

## Project Overview
The goal of this project is to develop an elastic face recognition application that uses AWS IaaS resources. The application automatically scales to meet demand, utilizing a deep learning model for image classification.

## Architecture
The application follows a three-tier architecture:
1. **Web Tier**: Handles incoming HTTP requests and communicates with the App Tier.
2. **App Tier**: Performs the actual face recognition using a pre-trained deep learning model.
3. **Data Tier**: Stores input images and classification results in AWS S3.

## Components

### Web Tier
- **Description**: Receives images via HTTP POST requests, sends them to the App Tier, and returns the classification results to the user.
- **Endpoint**: Listens on port 8000 for requests.
- **Input**: Accepts `.jpg` files with the key `inputFile`.
- **Output**: Returns results in the format `<filename>:<classification_results>`.
- **Scaling**: Includes an autoscaling controller that adjusts the number of App Tier instances based on request load.

### App Tier
- **Description**: Runs the deep learning model for face recognition.
- **Model**: Uses PyTorch-based models deployed on EC2 instances.
- **Scaling**: Automatically scales instances based on the number of pending requests, scaling between 0 and 20 instances.

### Data Tier
- **Description**: Manages persistent storage of images and recognition results.
- **Storage**: Utilizes AWS S3 with distinct buckets for input images and classification results.

## Setup and Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/your-repository.git
   cd your-repository

2. **Install Dependencies**:
   ```bash
   pip3 install torch torchvision torchaudio

3. **Deploy AWS Resources**:
- Set up EC2 instances, S3 buckets, and SQS queues as per the naming conventions specified.
- Follow the instructions to create and deploy AMIs for the App Tier.

## Usage
- Start the Web Tier: Launch the web instance and ensure it listens on port 8000.
- Send Requests: Use the provided workload generator to send requests to the Web Tier.
- View Results: Results are returned in plain text and can be viewed in the S3 output bucket.

## Testing
- Use the workload generator to validate the application's performance under different loads.
- Ensure that scaling behaves as expected, with the App Tier instances scaling up and down based on demand.

## Autoscaling Algorithm
- The autoscaling controller adjusts the App Tier instance count based on queue metrics, scaling out when demand increases and scaling in when demand decreases.

## License
- This project is part of the Cloud Computing course (CSE 546) and follows the guidelines and submission policies set by the instructor.
