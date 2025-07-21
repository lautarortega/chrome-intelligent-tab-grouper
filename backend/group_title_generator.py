import json
import ollama

class ClustersTitleGenerator():
    def __init__(self, clusters):
        self.clusters = clusters
    def run(self):
        titled_clusters = {}
        for cluster, tabs in self.clusters.items():
            titles = self.get_cluster_titles(tabs)
            urls = self.get_cluster_urls(tabs)
            prompt = f"""
            Generate a title for the a group of tabs which titles are: {titles} and urls are: {urls}
            Only return the title. Make sure it is short and concise. Not more than 3 words, best if 2 or 1 word.
            """
            response = ollama.generate(model='phi4-mini',prompt=prompt)
            cluster_title = response['response']
            titled_clusters[cluster_title] = tabs.keys()
        return titled_clusters

    def get_cluster_titles(self, cluster_tabs):
        titles = []
        for tab in cluster_tabs.values():
            title = tab['title']
            titles.append(title)
        return titles
    def get_cluster_urls(self, cluster_tabs):
        urls = []
        for tab in cluster_tabs.values():
            url = tab['url']
            urls.append(url)
        return urls



if __name__ == "__main__":
    with open("sample_data/group_title_generator.json", 'r') as file:
        sample_clusters = json.load(file)
        title_generator = ClustersTitleGenerator(sample_clusters)
        titled_clusters = title_generator.run()
        print(json.dumps(titled_clusters))