console.log("Extension opened");

document.addEventListener("DOMContentLoaded", async () => {
    const tabs = await chrome.tabs.query({
        currentWindow: true
    });

    console.log("Tabs in current window:", tabs);

    // Group tabs by hostname
    const hostnameGroups = new Map();

    tabs.forEach(tab => {
        if (tab.url) {
            const url = new URL(tab.url);
            let hostname = url.hostname;

            // Remove 'www.' if it exists
            if (hostname.startsWith("www.")) {
                hostname = hostname.slice(4);
            }

            // Split the hostname, remove the last element, and join the rest with a space
            const parts = hostname.split(".");
            if (parts.length > 1) {
                parts.pop(); // Remove the last element (e.g., 'com', 'org')
            }
            hostname = parts
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(" ");

            if (!hostnameGroups.has(hostname)) {
                hostnameGroups.set(hostname, { tabIds: [], count: 0 });
            }

            const group = hostnameGroups.get(hostname);
            group.tabIds.push(tab.id);
            group.count += 1; // Increment the counter for this hostname
        }
    });

    // Filter out groups with only one tab
    hostnameGroups.forEach((group, hostname) => {
        if (group.count <= 1) {
            hostnameGroups.delete(hostname);
        }
    });


    const groupButton = document.querySelector("#group-tabs-btn");
    groupButton.addEventListener("click", async () => {
        // Create tab groups for each hostname with more than one tab
        hostnameGroups.forEach(async (group, hostname) => {
            const groupId = await chrome.tabs.group({ tabIds: group.tabIds });
            await chrome.tabGroups.update(groupId, { title: hostname });
            console.log(`Grouped tabs for hostname: ${hostname}`);
        });
    });

    const ungroupButton = document.querySelector("#ungroup-tabs-btn");
    ungroupButton.addEventListener("click", async () => {
        // Query all tabs in the current window
        const allTabs = await chrome.tabs.query({ currentWindow: true });

        // Ungroup all tabs by setting their groupId to -1
        allTabs.forEach(async (tab) => {
            if (tab.groupId !== -1) {
                await chrome.tabs.ungroup(tab.id);
            }
        });

        console.log("All tabs have been ungrouped.");
    });
});