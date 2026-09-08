/**
 * VP Viimistlus ja Puhastus OÜ.
 *
 * Leht on staatiline, aga Worker peab olemas olema. Ilma main väljata ütleb
 * Cloudflare paneel "Variables cannot be added to a Worker that only has
 * static assets" ja muutujaid lisada ei saa.
 *
 * Siin on ka www suunamine. Faili public/_redirects sisse seda panna ei saa,
 * sest Workeri assets lubab seal ainult suhtelisi aadresse.
 *
 * Eelvaate aadressile (*.workers.dev) lisame X-Robots-Tag: noindex, muidu
 * indekseerib Google sama lehe kaks korda.
 */
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const host = url.hostname;

    if (host.startsWith("www.")) {
      url.hostname = host.slice(4);
      return Response.redirect(url.toString(), 301);
    }

    const vastus = await env.ASSETS.fetch(request);

    if (host.endsWith(".workers.dev")) {
      const paised = new Headers(vastus.headers);
      paised.set("X-Robots-Tag", "noindex, nofollow");
      return new Response(vastus.body, {
        status: vastus.status,
        statusText: vastus.statusText,
        headers: paised,
      });
    }

    return vastus;
  },
};
