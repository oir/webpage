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
        <a :href="paper['repo']" target="_blank" rel="noopener">
          <i class="fa fa-github lg"></i>
        </a>
      </span>
      <span v-if="'preprint' in paper">
        <a :href="paper['preprint']" target="_blank" rel="noopener">preprint</a>
      </span>
    </p>
  </p>
</div>
