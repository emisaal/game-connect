# GameConnect - README


## Introduction
Welcome to the GameConnect project! GameConnect is a Django-based web application that enables users not only to trade games but also provides access to exclusive articles related to gaming and more. 
This README file provides an overview of the project's structure and functionality.

## Project Structure
The GameConnect project is organized as follows:

- `gameapp/` - This directory contains Django models, views, and forms for the core functionality of the application, including user registration, login, game listing, and offers.
- `gameconnect/` - This directory contains project-specific settings and local configurations, including the Mailchimp API settings.
- `templates/` - This directory contains HTML templates for rendering the web pages.
- `manage.py` - The Django management script to interact with the project.
- `requirements.txt` - A list of Python packages required for the project.

## Functionalities
GameConnect offers a range of exciting functionalities that make it a hub for gamers looking to connect, trade games, and access exclusive articles:

### Authentication and User Management
- User registration and login.
- Custom login view.
- Change password functionality.
- User pages with active and inactive offers and notifications.
- User-specific actions (f.e. mark notifications as read).

### Main Page
- Display the latest game, article, and exchange offer on the main page.

### Game and Article Listing
- List games and articles.
- Order games by name and articles by the added date.
- Display game and article details.

### Exchange Offers and Market
- List active exchange offers.
- Filter exchange offers by game.
- Create and manage exchange offers.
- Make offers on existing exchange offers.
- Accept or reject customer offers.
- Email notifications for offer actions.

### Email Subscription
- Subscribe to a mailing list using the Mailchimp API.
- Send a welcome email to new subscribers.

### Game and Article Management (Admin)
- Create new games and articles with permission requirements.

With these diverse functionalities, GameConnect caters to gamers' needs for both trading games and staying informed with exclusive gaming articles. Get ready to connect, trade, and explore the gaming world with GameConnect!
