# Wall App

Wall App is a modern, responsive web application that allows users to create and share posts, engage in discussions through comments, and toggle between light and dark themes. Built with Flask and enhanced with rich text editing capabilities, it provides a seamless and interactive user experience.

## Features

### Post Management
- Create posts with rich text formatting
- Real-time post creation and display
- Posts are sorted chronologically (newest first)
- Permanent storage using JSON file system

### Rich Text Editor
- Full-featured Quill.js editor integration
- Support for text formatting (bold, italic, underline)
- Headers and text size options
- Ordered and unordered lists
- Text alignment controls
- Color and background styling
- Link, image, and video embedding

### Comments System
- Interactive comment sections for each post
- Real-time comment updates
- Relative timestamp display for comments
- Comment counter

### Theme System
- Toggle between light and dark themes
- Persistent theme preference storage
- Smooth transition animations
- Optimized colors for readability

### User Interface
- Clean and modern design
- Responsive layout for all device sizes
- Smooth animations and transitions
- Intuitive interaction patterns

## Technical Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Storage**: JSON file system
- **Rich Text Editor**: Quill.js
- **Icons**: Font Awesome
- **Animations**: GSAP
- **Fonts**: Google Fonts (Poppins, Montserrat)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd wall-app