# Project Management Dashboard

This repository contains a Streamlit application for visualizing and managing project data. The dashboard provides various charts and metrics to help track project status, duration, priority, and more.

## Overview

The Project Management Dashboard offers the following features:
- Total number of projects, average duration, median duration, and delayed projects count.
- Donut charts displaying the distribution of projects by priority and status.
- Scatter plot and bar charts showing the number of projects assigned to individuals and project components.
- Gantt chart to visualize the timeline of projects based on their status and priority.

## Features

- **Metrics:** Display key project metrics such as total projects, delayed projects, average duration, and median duration.
- **Donut Charts:** Visual representation of project distribution by priority and status.
- **Scatter Plot and Bar Charts:** Analysis of projects by responsible individuals and project components.
- **Gantt Chart:** Visual timeline of projects filtered by status, year range, and priority.

## Setup

### Prerequisites

Ensure you have the following installed:
- Python 3.7+
- Streamlit
- Pandas
- Altair

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/project-management-dashboard.git
    cd project-management-dashboard
    ```

2. Create and activate a virtual environment (optional but recommended):
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Place your `PM_Data.csv` file in the root directory of the project.

### Running the Application

To run the Streamlit application, use the following command:
```sh
streamlit run app.py
