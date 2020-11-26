# Course Project
## Project Proposal

- Project ID and title = 24 - Palette-based Photo Recolouring
- Link to GitHub repository - https://github.com/Digital-Image-Processing-IIITH/project-kanyaraasi
- Team members - 

| Team Member Name            |   Student ID Number       |
|-----------------------------|---------------------------|
| G. Sushanth Reddy           | 	20171172          |
| CH Pavan Kalyan Reddy       | 	20171205          |
| Rupa Nuthalakanti           | 	20171111          |
| CH Anudeep                  | 	20171042          |
| P.Pavan Chaitanya Reddy     | 	20171109          |

## Main goal(s) of the project

The main goal of the Project is to implement a simple, intuitive and interactive tool that allows non-experts to recolor an image by editing a color palette. 
It includes bulding a GUI that is easy to learn and understand, implementing an efficient algorithm for creating a color palette from an image
and implementing a novel color transfer algorithm that recolors the image based on a user-modified palette

## Problem definition (What is the problem? How will things be done?)

- Research and commercial software offer a myriad of tools for manipulating the colors in photographs. Unfortunately these tools remain largely inscrutable to non-experts. 
- Many features like the “levels tool” in software like Photoshop and iPhoto require the user to interpret histograms and to have a good mental model of how color spaces like RGB work, so non-experts have weak intuition
  about their behavior. 
- There is a natural tradeoff between ease of use and range of expressiveness, so for example a simple hue slider, while easier to understand and manipulate than the levels tool,
  offers substantially less control over the resulting image. 
- From this project, a tool is introduced that is easy for novices to learn while offering a broad expressive range.
- Our approach specifies both the colors to be manipulated and the modifications to these colors via a color palette – a small set of colors that digest the full range of colors in the image. Given an image, we generate a suitable palette. 
- The user can then modify the image by modifying the colors in the palette.
- The image is changed globally such that the chosen colors are interpolated exactly with a smooth falloff in color space expressed through
  radial basis functions.
- These operations are performed in LAB color space to provide perceptual uniformity in the falloff. 
- Our color transfer function is tightly coupled with a subtle GUI affordance that together ensure monotonicity in the
  resulting changes in luminance. 
- This kind of color editing interface offers the best creative freedom when the user has interactive feedback while they explore various options.



## Results of the project (What will be done? What is the expected result?)

A user-friendly interactive tool which enables the user(non-expert on image processing) to recolor an image by adding a color pallete. 

## What are the project milestones and expected timeline?

| Event                       			               | Date                      |
|--------------------------------------------------------------|---------------------------|
| Color palette and matching algorithms implementation         | 28th October 2020         |
| GUI implementation                                           | 10th November 2020        |
| Final Project tool and report submission            	       | 18th November 2020        |


## Is there a dataset that you require? How do you plan to get it?

Yes, we need dataset. There are plenty of RGB images that can be downloaded from the internet.
