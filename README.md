# SW_Sec_Project

This repository contains the code that's part of the paper titled "SoK: Workerounds - Categorizing Service Worker Attacks and Mitigations" that wold be published in Euro S&P 2022 conference. 

***Paper Abstract***

Service Workers (SWs) are a powerful feature at the core of Progressive Web Apps, namely web applications that can continue to function when the user’s device is offline and that have access to device sensors and capabilities previously accessible only by native applications. During the past few years, researchers have found a number of ways in which SWs may be abused to achieve different malicious purposes. For instance, SWs may be abused to build a web-based botnet, launch DDoS attacks, or perform cryptomining; they may be hijacked to create persistent cross-site scripting (XSS) attacks; they may be leveraged in the context of side-channel attacks to compromise users’ privacy; or they may be abused for phishing or social engineering attacks using web push notifications-based malvertising.

In this paper, we reproduce and analyze known attack vectors related to SWs and explore new abuse paths that have not previously been considered. We systematize the attacks into different categories, and then analyze whether, how, and estimate when these attacks have been published and mitigated by different browser vendors. Then, we discuss a number of open SW security problems that are currently unmitigated, and propose SW behavior monitoring approaches and new browser policies that we believe should be implemented by browsers to further improve SW security. Furthermore, we implement a proof-of-concept version of several policies in the Chromium code base, and also measure the behavior of SWs used by highly popular web applications with respect to these new policies. Our measurements show that it should be feasible to implement and enforce stricter SW security policies without a significant impact on most legitimate production SWs

Below is a brief description of the modules in this project

***<li> SWSec_Chromium***: This folder contains the instrumentation changes that were made to Chromium to enable logging information related to service worker and enabling dynamic monitoring of service workers. More details can be found in the readme file inside the folder.

***<li> SWSec_Crawler***: This folder consists of the code related to running crawlers using NodeJS Puppeteer framework and the code used to scale the crawling to run on multiple docker containers including the files required to build the corresponding docker image.
  
***<li> SWSec_Data***: this fodler contains seed URLs that were used for the cralwing and measurement.

***<li> SWSec_Analysis***: This fodler consists of helper scripts that were used to report measurements by parsing the logs collected by the crawler module and generating graphs reported in the paper.


The attacks reproduced and new attacks that are proposed can be accessed in the link: https://demopwa.github.io/sw_index.html. This link contains demos of the attacks with the browser version that the attacks work and their source code. These online demos could serve as a test bed to check new versions of browser to check if they are vulnerable.  
