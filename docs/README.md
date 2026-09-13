Hi! I am an AI Research Scientist at [Bloomberg](https://www.bloomberg.com/company/stories/tag/data-science/).

Before that, I was a PhD student at [CS](http://www.cs.cornell.edu/) at [Cornell University](http://www.cornell.edu/), advised by [Claire Cardie](http://www.cs.cornell.edu/home/cardie/).

And before that, I was an undergrad at [Bogazici University](http://www.boun.edu.tr/en_US), pursuing my BS in [Computer Engineering](https://cmpe.boun.edu.tr/) and BA in [Math](http://math.boun.edu.tr/).


# Publications

<script>
  Vue.createApp({
      data() {
        return {
          papers: null,
        };
      },
      created() {
        fetch("papers.yaml")
          .then((res) => res.text())
          .then((text) => {
              this.papers = jsyaml.load(text)
          })
          .catch((e) => console.error(e));
      }
  }).mount('#main');
</script>

<div v-if="papers">
    <p v-for="paper in papers">
      <span class="paper-title">
        <a :href="paper['link']" target="_blank" rel="noopener"> {{ paper['title'] }} </a>
      </span>
      <span class="paper-authors"> {{ paper["authors"] }} </span>
      <span v-if="typeof paper['venue'] === 'string'" class="paper-venue"> {{ paper["venue"] }} </span>
      <span v-if="Array.isArray(paper['venue'])">
        <span class="paper-venue" v-for="venue in paper['venue']"> {{ venue }} </span>
      </span>
      <span v-if="'repo' in paper">
        <a :href="paper['repo']" target="_blank" rel="noopener" :aria-label="'code repository for ' + paper['title']">
          <svg class="gh-mark" viewBox="0 0 16 16" aria-hidden="true"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>
        </a>
      </span>
      <span v-if="'preprint' in paper">
        <a :href="paper['preprint']" target="_blank" rel="noopener">preprint</a>
      </span>
    </p>
  </p>
</div>
