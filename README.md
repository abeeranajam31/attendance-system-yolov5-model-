## 1 Introduction

Advancements in Artificial Intelligence (AI) have opened
new avenues in various sectors, including education. Man-
ual attendance recording in educational institutions is prone
to inaccuracies and is a time-consuming process. Our AI-
based system leverages Google’s FaceNet technology to au-
tomate attendance, ensuring high accuracy and efficiency.

## 2 Background

FaceNet’s deep learning framework has proven effective
in various applications, particularly in identity verification
through facial recognition. This technology’s adaptation
into an attendance management system proposes a stream-
lined approach for academic instit

## 3 Functionality 

The application’s core functionality
includes interfacing with the device’s gallery for image se-
lection and integrating a custom date picker for select-
ing the attendance date. The user interface is designed to
be intuitive, allowing users to easily navigate through the
gallery, select an image, and choose the corresponding date
using a calendar widget. These elements are critical for
ensuring the correct data is captured for processing atten-
danc

## • Image and Date Reception Endpoint:

A dedicated
POST endpoint is established to handle incoming data
from the mobile application. This endpoint is respon-
sible for parsing the JSON payload to extract the en-
coded image and the attendance date. The image un-
dergoes decoding from its base64 format back into a
binary image format suitable for processing.
