class WikiSolver {
  constructor(onProgress, onComplete, onError) {
    this.onProgress = onProgress;
    this.onComplete = onComplete;
    this.onError    = onError;
    this.cancelled  = false;
  }

  cancel() { this.cancelled = true; }

  async solve(startRaw, endRaw) {
    this.cancelled = false;

    let start, end;
    try {
      [start, end] = await Promise.all([
        this._normalizeTitle(startRaw),
        this._normalizeTitle(endRaw),
      ]);
    } catch (e) {
      this.onError('Network error while looking up pages. Check your connection.');
      return;
    }

    if (!start) { this.onError(`Wikipedia page not found: "${startRaw}"`); return; }
    if (!end)   { this.onError(`Wikipedia page not found: "${endRaw}"`);   return; }
    if (start === end) { this.onComplete([start], 1); return; }

    // parent[title] = the title that discovered it (null for start)
    const parent  = new Map([[start, null]]);
    const visited = new Set([start]);
    const queue   = [start];

    while (queue.length > 0 && !this.cancelled) {
      const current = queue.shift();
      this.onProgress(current, visited.size);

      let links;
      try {
        links = await this._getLinks(current);
      } catch (e) {
        // skip pages that error out — transient network issue
        continue;
      }

      if (this.cancelled) return;

      for (const link of links) {
        if (visited.has(link)) continue;
        visited.add(link);
        parent.set(link, current);

        if (link === end) {
          this.onComplete(this._buildPath(parent, start, end), visited.size);
          return;
        }

        queue.push(link);
      }
    }

    if (!this.cancelled) {
      this.onError('No path found — the destination may not be reachable via Wikipedia links.');
    }
  }

  _buildPath(parent, start, end) {
    const path = [];
    let node = end;
    while (node !== null) {
      path.unshift(node);
      node = parent.get(node);
    }
    return path;
  }

  async _normalizeTitle(title) {
    const url = `https://en.wikipedia.org/w/api.php?action=query&titles=${encodeURIComponent(title)}&redirects=1&format=json&origin=*`;
    const res  = await fetch(url);
    const data = await res.json();
    const page = Object.values(data.query.pages)[0];
    if ('missing' in page) return null;
    return page.title;
  }

  async _getLinks(title) {
    const links = [];
    let cont = null;

    do {
      let url = `https://en.wikipedia.org/w/api.php?action=query&titles=${encodeURIComponent(title)}&prop=links&pllimit=max&plnamespace=0&format=json&origin=*`;
      if (cont) url += `&plcontinue=${encodeURIComponent(cont)}`;

      const res  = await fetch(url);
      const data = await res.json();
      const page = Object.values(data.query.pages)[0];

      if (page.links) {
        for (const l of page.links) links.push(l.title);
      }

      cont = data.continue?.plcontinue ?? null;
    } while (cont && !this.cancelled);

    return links;
  }
}
