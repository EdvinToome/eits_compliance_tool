# E-ITS Compliance Auditor

Welcome to the E-ITS Compliance Auditor repository! This automated management and compliance tool is designed to audit systems according to the Estonian Information Security Standard (E-ITS). Below you will find detailed instructions on setting up the project, including all necessary dependencies, installation steps, and how to start the server.

## Table of Contents
1. [Dependencies](#dependencies)
2. [Installation](#installation)
3. [Environment Configuration](#environment-configuration)
4. [Running the Application](#running-the-application)
5. [Usage](#usage)
6. [Contributing](#contributing)
7. [License](#license)
8. [Research paper](#research-paper)
9. [TODO](#todo)

## Dependencies

Before you begin, ensure you have the following dependencies installed on your system:

1. **nmap**: A network scanning tool used for discovering hosts and services on a computer network.
2. **PostgreSQL**: A powerful, open-source object-relational database system.

## Installation

Follow these steps to install and set up the project:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/EdvinToome/eits_compliance_tool
   cd eits_compliance_tool
   ```

2. **Create a virtual environment:**

   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```

4. **Install the required Python packages:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Run database migrations:**

   ```bash
   python3 manage.py migrate
   ```

## Environment Configuration

Configure your database and other environment settings by following these steps:

1. **Create a `.env` file:**

   Copy the contents of `env.example` to a new file named `.env`.

   ```bash
   cp env.example .env
   ```

2. **Configure the database:**

   Edit the `.env` file to set your PostgreSQL database configuration:

   ```
   DATABASE_NAME=yourdatabase
   DATABASE_USER=youruser
   DATABASE_PASSWORD=yourpassword
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   ```

## Running the Application

1. **Collect E-ITS controls:**

   To retrieve E-ITS controls, run the following command:

   ```bash
   python manage.py collect_eits_controls
   ```

2. **Start the server:**

   Start the development server with:

   ```bash
   python manage.py runserver
   ```

## Usage

Once the server is running, you can access the application at `http://localhost:8000/admin`. Use the web interface to manage and audit systems according to the Estonian Information Security Standard.

## Contributing

See the `CONTRIBUTING` file for more details.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Research paper

For an in-depth understanding of the development and capabilities of this tool, please refer to the research conducted on this project. The research paper titled "Automaatkontrolli võimekusega Eesti Infoturbestandardi rakendaja haldustöövahendi arendamine" provides detailed insights and is available at TalTech's digital library.

[Read the full research paper here](https://digikogu.taltech.ee/et/Item/2e79b171-a500-4160-950b-ad01b28c1307)

## TODO
- Add more automated scripts.
- Add REST API support for running audits and retrieving results.
- Use Rust to write some modules for scripts.
- Add a pretty front-end interface using some SPA framework.
- Add other UML support.
- Implement machine learning for auditing semi-automated controls.
- Add Dockerfile.


---

Thank you for using the E-ITS Compliance Auditor! If you have any questions or need further assistance, please feel free to open an issue or contact us.


