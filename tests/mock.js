(() => {
  const store = new Map(); const listeners = new Set(); let n = 0;
  const fire = () => setTimeout(() => listeners.forEach(f => f()), 0);
  const segs = (p) => p.split("/").filter(Boolean);
  function docRef(path) {
    return { id: segs(path).pop(), path,
      async get() { const d = store.get(path); return { exists: !!d, id: segs(path).pop(), data: () => d && JSON.parse(JSON.stringify(d)) }; },
      async set(o) { store.set(path, JSON.parse(JSON.stringify(o))); fire(); },
      async delete() { store.delete(path); fire(); },
      collection(c) { return colRef(path + "/" + c); } };
  }
  function colRef(path, q = {}) {
    const run = () => {
      let docs = [...store.entries()].filter(([k]) => k.startsWith(path + "/") && segs(k).length === segs(path).length + 1)
        .map(([k, v]) => ({ id: segs(k).pop(), data: () => JSON.parse(JSON.stringify(v)) }));
      if (q.where) docs = docs.filter(d => d.data()[q.where[0]] === q.where[2]);
      if (q.order) docs.sort((a, b) => (a.data()[q.order[0]] > b.data()[q.order[0]] ? 1 : -1) * (q.order[1] === "desc" ? -1 : 1));
      if (q.limit) docs = docs.slice(0, q.limit);
      return { docs, metadata: { fromCache: false } };
    };
    return { path,
      async add(o) { const id = "d" + (++n); store.set(path + "/" + id, JSON.parse(JSON.stringify(o))); fire(); return { id }; },
      doc(id) { return docRef(path + "/" + id); },
      where(f, op, v) { return colRef(path, { ...q, where: [f, op, v] }); },
      orderBy(f, d) { return colRef(path, { ...q, order: [f, d] }); },
      limit(k) { return colRef(path, { ...q, limit: k }); },
      async get() { return run(); },
      onSnapshot(cb) { const f = () => cb(run()); listeners.add(f); setTimeout(f, 0); return () => listeners.delete(f); } };
  }
  const db = { doc: docRef, collection: (p) => colRef(p) };
  const user = { async me() { return window.__member ? { id: "u-member", name: "Test Member", canEdit: false, isOwner: false } : { id: "u-officer", name: "Test Officer", canEdit: true, isOwner: false }; },
    async profiles(ids) { return Object.fromEntries(ids.map(i => [i, { name: i === "u-officer" ? "Test Officer" : "someone" }])); } };
  const sample = async (prompt, opts) => { window.__lastPrompt = prompt; (window.__calls = window.__calls || []).push((opts.images || []).length);
    return { text: 'Here you go: {"power_millions": 14.4, "deployed": "Helix", "resonance": ["Otta", "Thor"], "mystling": {"name": "Death Mage", "stars": null}, ' +
      '"gear": {"weapon": {"set": "Dragoon", "quality": "Chaotic"}, "amulet": {"set": "Griffin", "quality": "Chaotic"}, "ring": {"set": null, "quality": "Chaotic"}, "helmet": {"set": "Dragoon", "quality": "Chaotic"}, "armor": {"set": "Oracle", "quality": "Chaotic"}, "boots": {"set": "Dragoon", "quality": "Bogus"}}, ' +
      '"runes": {"blessing": [{"name": "Revive", "quality": "Legendary"}, {"name": "Not A Rune", "quality": null}], "enhancement": [], "ability": [], "etched": []}, ' +
      '"behavior": {"range": "Long", "movement": "Offense"}, "unclear": ["etched runes cut off"]}' }; };
  sample.limits = async () => ({ images: true });
  window.__store = store; window.__fire = fire;
  if (window.__preseed) for (const [k, v] of Object.entries(window.__preseed)) store.set(k, v);
  window.claude = { use: async (name) => ({ db, user, sample }[name] || null) };
})();
