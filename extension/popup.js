console.log("Extension opened");

document.addEventListener("DOMContentLoaded", async () => {
    const tabs = await chrome.tabs.query({
        currentWindow: true
    });

    const tabsJson = tabs.reduce((result, tab) => {
        if (tab.url) {
            result[tab.id] = {
                title: tab.title,
                url: tab.url
            };
        }
        return result;
    }, {});

    console.log(JSON.stringify(tabsJson, null, 2));

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

    const smartGroupButton = document.querySelector("#smart-group-tabs-btn");
    smartGroupButton.addEventListener("click", async () => {
        console.log("Smart grouping started...");
        const allTabs = await chrome.tabs.query({ currentWindow: true });

        const payloadTabs = allTabs.map(tab => ({
            id: String(tab.id),
            url: tab.url,
            title: tab.title || "",
            body: "" // We don't have body content access yet easily without content script
        }));

        try {
            const response = await fetch("http://localhost:8000/api/v1/group", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payloadTabs)
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            const data = await response.json();
            console.log("Grouping Data:", data);

            // Apply groups
            for (const group of data.groups) {
                if (group.tabs.length > 0) {
                    const tabIds = group.tabs.map(t => parseInt(t.id));
                    const chromeGroupId = await chrome.tabs.group({ tabIds: tabIds });
                    await chrome.tabGroups.update(chromeGroupId, { title: group.title });
                    console.log(`Grouped "${group.title}" with tabs: ${tabIds}`);
                }
            }

        } catch (error) {
            console.error("Failed to group tabs smartly:", error);
            alert("Failed to group tabs. Is the backend running?");
        }
    });
});