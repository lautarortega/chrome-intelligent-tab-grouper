# Chrome Intelligent Tab Grouper

A Chrome extension that intelligently groups and ungroups tabs based on their hostnames. This extension helps organize your browsing experience by grouping related tabs together and providing an option to ungroup them when needed.

## Features

- **Group Tabs**: Automatically groups tabs in the current window by their hostnames.
- **Ungroup Tabs**: Allows you to ungroup all tabs in the current window with a single click.
- **Hostname Simplification**: Removes `www` and top-level domains (e.g., `.com`, `.org`) for cleaner group titles.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/chrome-intelligent-tab-grouper.git
   ```
2. Open Chrome and navigate to `chrome://extensions/`.
3. Enable **Developer mode** (toggle in the top-right corner).
4. Click **Load unpacked** and select the `extension` folder within this repository.

## Usage

1. Click on the extension icon in the Chrome toolbar to open the popup.
2. Use the **Group Tabs** button to group tabs by hostname.
3. Use the **Ungroup All Tabs** button to ungroup all tabs.

## File Structure

- `extension/`: Directory containing all extension-related files
  - `manifest.json`: Defines the extension's metadata and permissions.
  - `popup.html`: The HTML file for the extension's popup interface.
  - `popup.js`: Contains the logic for grouping and ungrouping tabs.
- `README.md`: Documentation for the project.

## Permissions

This extension requires the following permissions:
- `tabs`: To query and manipulate tabs.
- `tabGroups`: To create and manage tab groups.

## Roadmap

- [ ] **Integrate Machine Learning for Tab Grouping**:
  - Develop a machine learning model that can analyze tab data (e.g., URLs, titles) and suggest groups with meaningful names.
  - Create an API endpoint to host the ML model and make it accessible to the Chrome extension.
  - Update the extension to send tab data to the API and process the response to create groups.

- [ ] **Localization**:
  - Add support for multiple languages to make the extension accessible to a broader audience.

- [ ] **Testing and Reliability**:
  - Add unit tests and integration tests to ensure the extension works reliably.
  - Test the API integration with various datasets.

- [ ] **UI/UX Enhancements**:
  - Improve the popup interface for better usability.

## Contributing

Feel free to fork this repository and submit pull requests for new features or bug fixes.

## License

This project is licensed under the [MIT License](LICENSE).
