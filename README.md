# Code Mapper

Code Mapper is an innovative tool designed to visualize the geographic distribution of contributors in GitHub repositories. It aims to highlight the global influence and reach of open-source projects, providing insights into collaboration patterns, community dynamics, and inclusivity within the FOSS (Free and Open Source Software) ecosystem.

This repository hosts the source code for Code Mapper, including backend scripts, frontend assets, and the trained machine learning model used for geolocation predictions. **Please note that the actual data used by the live application is not provided in this repository due to the sensitive nature of the information (e.g., contributor's names and predicted locations)**.

## Live Application

Access the live application at [https://codemapper.alwaysdata.net](https://codemapper.alwaysdata.net) to explore the geographic distribution of contributors across various GitHub repositories.

## Features

- Visualize the geographic distribution of repository contributions on an interactive map.
- Discover the countries or regions involved in open source development.
- Detailed information on contributions by location

## Repository Structure

- `scriptAndDatabase/` - Contains all backend scripts necessary for fetching and processing GitHub data.
- `scriptAndDatabase/database/` - Contains all (non-sensitive) data for repository locations. 
- `scriptAndDatabase/loadBackendData/` - Houses PHP scripts that connect the backend scripts to the frontend. 
- `scriptAndDatabase/MachineLearning/` - Contains the training script, and the evaluation script. Note that we did not include the training data for privacy reasons.
- `scriptAndDatabase/userDB/` - Contains data used to compute a contributor's location and determine the repository contributions distribution. Note that we did not include any user data for privacy reasons.
- `js/` - Houses the frontend code including the interactive map for the web interface.
- `css/` - The CSS for the web interface.
- `images/` - Static images used for the web interface.
- `docs/` - Houses more detailed documentation on each script and data file. 

## Installation and Local Setup

This section describes how to set up Code Mapper for local development purposes.

**Important Note on Local Deployment**

Please be aware that when running this application locally, you will not experience the full functionality available in the live version. The key datasets, particularly those containing sensitive information regarding contributors' names and predicted locations, are not included in this repository due to privacy and security reasons.

As a result, certain features might not perform as expected. This limitation is in place to respect privacy and ensure the security of individuals' data.

We encourage users to view the live application for the complete experience and use the local version for development and testing purposes only. Thank you for your understanding and cooperation in maintaining the privacy of contributors' data.

### Prerequisites

- Git
- Python 3.x
- pip (Python package installer)

### Clone the Repository and Install Python Dependencies

To get started, clone the repository to your local machine:

```bash
git clone https://github.com/jaslatendresse/codemapper.git
cd codemapper
pip install -r requirements.txt
```

### Download the Trained Model

1. Download the trained model [here](https://drive.google.com/file/d/18z3l-dfCNDYfJfk-FdGjxwszTKXgM1qA/view?usp=share_link)

2. Place the trained model file in `scriptAndDatabase/MachineLearning/`.

### Backend setup

To run the app locally, you'll need to set up a **GitHub personal access token**. 

1. **Go to GitHub's Token Settings**:
   - Log in to GitHub and click [here](https://github.com/settings/tokens) to go directly to your 'Personal access tokens' settings.
   - Click `Generate new token`.

2. **Create Your Token**:
   - Assign a `Note` for your token (like "code-mapper usage").
   - Select the scopes for your project needs, typically `repo`.
   - Click `Generate token` at the bottom.

3. **Copy Your Token**:
   - Save your token somewhere safe. Once you leave the page, you won't see it again.

4. **Open `config.json`**:
   - In the project root directory, find the `config.json` file.

5. **Add Your Token**:
   - Replace `YOUR_PERSONAL_ACCESS_TOKEN` with your token in this section:

   ```json
   {
     "GH_TOKEN": "YOUR_PERSONAL_ACCESS_TOKEN"
   }

Next, **you'll need to set up a local server**. For Windows users, WAMP is a great option, while macOS will need to use MAMP. Below are the installation and usage instructions for both:

#### WAMP (Windows)

##### Step 1: Download WAMP Server
- Visit the [WAMP Server website](http://www.wampserver.com/en/) and select the version that's compatible with your Windows architecture (32-bit or 64-bit).

##### Step 2: Install WAMP Server
- Open the downloaded file and follow the prompts. Choose your destination folder (default is `C:\wamp64`), and select your default browser if asked.

##### Step 3: Check Server Status
- Launch WAMP. A green system tray icon indicates that all services are running.

##### Step 4: Access Your Localhost
- Click the WAMP system tray icon and select 'localhost'. Your default browser will display the WAMP server landing page.

##### Step 5: Place Your Application Files
- Navigate to the `www` directory inside your WAMP installation folder and create a new folder for your application's files.

##### Step 6: Access Your Application
- In your browser, navigate to `http://localhost/codemapper`.

#### MAMP (macOS)

##### Step 1: Download MAMP
- Go to the [MAMP website](https://www.mamp.info/en/mamp/mac/) and download the free version.

##### Step 2: Install MAMP
- Open the downloaded file and drag the MAMP folder (not MAMP PRO) to your Applications folder.

##### Step 3: Launch MAMP
- Open MAMP from your Applications folder and click 'Start Servers'. Green status lights indicate running services.

##### Step 4: Access Your Localhost
- Click 'Open WebStart page' in MAMP. Your default browser will show the MAMP landing page.

##### Step 5: Place Your Application Files
- Put your application files in the `MAMP/htdocs/` directory in your MAMP folder.

##### Step 6: Access Your Application
- In your browser, navigate to `http://localhost:8888/codemapper`. MAMP uses port 8888 by default.


## Contributing

We welcome contributions to Code Mapper. If you're interested in contributing, please take a look at our CONTRIBUTING.md file to learn about how to propose improvements, report bugs, or enhance the application.

## Contact

For any inquiries or further information, please open an issue on GitHub.



