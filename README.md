## KPI Mobile First

### Background (from a city council resolution) and measurement procedure

The Mobile First Principle states that the presentation of services on mobile devices should have the highest priority. At the same time, they are always designed to be user-friendly for other relevant workplaces or end devices.

To determine the KPI, the number of compliant services is recorded and put in relation to the total number of services for which the mobile first principle is relevant. This results in the relative share of services in the sense of the goal.

Measurement method: Google's Lighthouse tool checks web applications for mobile capability. The result is an indicator between 0 and 1, where 1 stands for 100% compliance with the test criteria (e.g. performance, accessibility, SEO capability, best practices, progressive web application). The mean value of the 5 criteria is used here. The desktop version is also tested for comparison.

Format of urlCsvFile: 
1. Column: Name of the Site
2. Column: Url

### Usage as web app

./app.py

http://<host>:5000/ and follow inststurctions.

Note: It is a single user app. The web app is a small wrapper of the cli runLighthouse.py app, which is file based. The purpose of the web app is to run the cli app in a container.

