#!/usr/bin/env python3
"""Build 5 Spanish-language city pages for top Hispanic-population metros.

Each page:
- /es/renta-de-banos-portatiles-{city}-{state}/index.html
- lang="es", hreflang annotations to English equivalent
- Locale es-US, schema markup with inLanguage
- Phone-only CTAs in Spanish
- Internal links to English city + service pages (those are still in English)
"""
from __future__ import annotations
import os

# (slug, en_slug, city, state, state_full, lat, lon,
#  intro_es, neighborhoods_es, anchor_venues_es, regulatory_es)
CITIES = [
    {
        "slug": "renta-de-banos-portatiles-houston-tx",
        "en_slug": "porta-potty-rental-houston-tx",
        "city": "Houston",
        "state": "TX",
        "state_full": "Texas",
        "state_full_es": "Texas",
        "lat": 29.7604,
        "lon": -95.3698,
        "zip": "77002",
        "intro_es": "Renta de baños portátiles en Houston, Texas. Servicio el mismo día para construcción, bodas, fiestas, festivales, y emergencias. Cubrimos todo el condado de Harris &mdash; desde el Downtown y el Galleria hasta Pasadena, Pearland y Sugar Land. Hablamos español. Llame y le cotizamos en 60 segundos.",
        "neighborhoods_es": [
            "Downtown Houston", "The Heights", "Midtown", "Montrose", "River Oaks",
            "Galleria/Uptown", "Medical Center", "Energy Corridor", "Memorial",
            "EaDo (East Downtown)",
        ],
        "anchor_venues_es": "Discovery Green, Minute Maid Park, NRG Stadium, Toyota Center, el Texas Medical Center",
        "regulatory_es": "Las construcciones en Texas siguen las normas OSHA 29 CFR 1926.51. Entregamos la documentación de proporciones OSHA con cada cotización. El verano de Houston (mayo a septiembre) requiere productos resistentes al calor &mdash; los incluimos sin cargo extra.",
        "use_cases_es": [
            ("Construcción", "Cumplimiento OSHA, servicio semanal o dos veces por semana, contratos mensuales para proyectos largos."),
            ("Bodas y eventos", "Tráileres de baños de lujo con aire acondicionado, inodoros con descarga, agua caliente."),
            ("Festivales y conciertos", "Servicio nocturno para eventos de varios días, unidades ADA en cada cluster, estaciones de lavado de manos."),
            ("Emergencias", "Despacho 24 horas. Entrega el mismo día en la mayoría del condado de Harris."),
            ("Petrolero", "Servicio en la cuenca del Eagle Ford y el Permian, con camiones 4x4 para sitios remotos."),
        ],
    },
    {
        "slug": "renta-de-banos-portatiles-los-angeles-ca",
        "en_slug": "porta-potty-rental-los-angeles-ca",
        "city": "Los Angeles",
        "state": "CA",
        "state_full": "California",
        "state_full_es": "California",
        "lat": 34.0522,
        "lon": -118.2437,
        "zip": "90013",
        "intro_es": "Renta de baños portátiles en Los Angeles, California. Servicio el mismo día para producción de cine y TV, construcción, bodas en la playa, festivales, y emergencias. Cubrimos todo el condado de LA &mdash; Hollywood, Venice, Downtown, Long Beach, Glendale. Cumplimos con Cal/OSHA. Hablamos español.",
        "neighborhoods_es": [
            "Downtown LA", "Hollywood", "Venice", "Beverly Hills", "Santa Monica",
            "West Hollywood", "Silver Lake", "Echo Park", "Mid-Wilshire", "South LA",
        ],
        "anchor_venues_es": "Crypto.com Arena, the Hollywood Bowl, the Greek Theatre, SoFi Stadium, Dodger Stadium",
        "regulatory_es": "California cumple con Cal/OSHA Título 8 §1526 &mdash; las proporciones son más estrictas que el OSHA federal. Usamos las tablas de Cal/OSHA por defecto. Para producción cinematográfica ofrecemos honeywagons (tráileres con cuartos privados) con cumplimiento NDA.",
        "use_cases_es": [
            ("Producción de cine y TV", "Honeywagons para talento, baños estándar para el equipo, cumplimiento NDA, camiones sin marcas si es necesario."),
            ("Construcción", "Proporciones Cal/OSHA, documentación para inspecciones, servicio dos veces por semana en sitios grandes."),
            ("Bodas y eventos", "Tráileres de lujo para bodas en la playa, viñedos, y propiedades privadas."),
            ("Festivales", "Coachella, Stagecoach, festivales del valle &mdash; servicio nocturno y cluster placement."),
            ("Emergencias", "Respuesta 24 horas para fallas de plomería, refugios de emergencia, e incendios."),
        ],
    },
    {
        "slug": "renta-de-banos-portatiles-miami-fl",
        "en_slug": "porta-potty-rental-miami-fl",
        "city": "Miami",
        "state": "FL",
        "state_full": "Florida",
        "state_full_es": "Florida",
        "lat": 25.7617,
        "lon": -80.1918,
        "zip": "33131",
        "intro_es": "Renta de baños portátiles en Miami, Florida. Servicio el mismo día para construcción, bodas, eventos, festivales, y respuesta a huracanes. Cubrimos todo el condado de Miami-Dade &mdash; Downtown, Brickell, Miami Beach, Hialeah, Miami Gardens. Anclajes para huracanes incluidos de junio a noviembre. Hablamos español.",
        "neighborhoods_es": [
            "Downtown Miami", "Brickell", "South Beach", "Coconut Grove", "Coral Gables",
            "Wynwood", "Little Havana", "Edgewater", "Mid-Beach", "Allapattah",
        ],
        "anchor_venues_es": "Hard Rock Stadium, Kaseya Center, Miami Beach Convention Center, Bayfront Park",
        "regulatory_es": "Florida sigue las normas OSHA federales. La temporada de huracanes (junio a noviembre) requiere kits de anclaje para vientos &mdash; los incluimos sin cargo extra. Para eventos cancelados por aviso de tormenta, no cobramos cargo de cancelación si avisa con 72 horas.",
        "use_cases_es": [
            ("Construcción de torres", "Houston Texas y Miami tienen las pipelines de construcción de rascacielos más grandes del país. Cumplimiento OSHA y unidades de gancho de grúa."),
            ("Eventos y festivales", "Art Basel, Miami Music Week, Ultra Music Festival &mdash; servicio nocturno, unidades ADA."),
            ("Bodas en la playa", "Tráileres de baños de lujo con aire acondicionado para playas y propiedades frente al mar."),
            ("Respuesta a huracanes", "Despliegue de 24 horas, registrados en SAM.gov para contratos federales y estatales de emergencia."),
            ("Refugios y centros de evacuación", "Capacidad de despliegue rápido para escuelas y centros comunitarios convertidos en refugios."),
        ],
    },
    {
        "slug": "renta-de-banos-portatiles-san-antonio-tx",
        "en_slug": "porta-potty-rental-san-antonio-tx",
        "city": "San Antonio",
        "state": "TX",
        "state_full": "Texas",
        "state_full_es": "Texas",
        "lat": 29.4241,
        "lon": -98.4936,
        "zip": "78205",
        "intro_es": "Renta de baños portátiles en San Antonio, Texas. Servicio el mismo día para construcción, eventos en el River Walk, bodas, bases militares (JBSA), Fiesta San Antonio en abril, y emergencias. Cubrimos todo el condado de Bexar. Registrados en SAM.gov para contratos militares. Hablamos español.",
        "neighborhoods_es": [
            "Downtown San Antonio", "King William", "Southtown", "Pearl District",
            "Stone Oak", "Alamo Heights", "Olmos Park", "Medical Center", "South Side",
            "East Side",
        ],
        "anchor_venues_es": "the Alamo, the River Walk, the Frost Bank Center, AT&amp;T Center, Lackland Air Force Base, Fort Sam Houston",
        "regulatory_es": "Texas sigue OSHA 1926.51. Las bases militares de Joint Base San Antonio requieren registro SAM.gov y conductores con preparación contractual &mdash; lo tenemos. Fiesta San Antonio (la última semana de abril) genera demanda alta &mdash; reserve con anticipación.",
        "use_cases_es": [
            ("Construcción", "Cumplimiento OSHA, contratos mensuales para proyectos largos."),
            ("Eventos en el River Walk", "Festivales y eventos a lo largo del River Walk &mdash; tráileres de lujo y unidades estándar."),
            ("Fiesta San Antonio", "Servicio para los eventos de Fiesta cada abril &mdash; cluster placement y servicio nocturno."),
            ("Bases militares (JBSA)", "Registrados en SAM.gov, conductores entrenados en protocolos de acceso a bases."),
            ("Bodas", "Tráileres de baños de lujo para bodas en estancias y propiedades privadas en Hill Country."),
        ],
    },
    {
        "slug": "renta-de-banos-portatiles-phoenix-az",
        "en_slug": "porta-potty-rental-phoenix-az",
        "city": "Phoenix",
        "state": "AZ",
        "state_full": "Arizona",
        "state_full_es": "Arizona",
        "lat": 33.4484,
        "lon": -112.0740,
        "zip": "85004",
        "intro_es": "Renta de baños portátiles en Phoenix, Arizona. Servicio el mismo día para construcción, eventos, bodas, festivales en el desierto, y emergencias. Cubrimos todo el condado de Maricopa &mdash; Phoenix, Mesa, Tempe, Chandler, Scottsdale, Glendale. Productos resistentes al calor incluidos de mayo a septiembre. Hablamos español.",
        "neighborhoods_es": [
            "Downtown Phoenix", "Arcadia", "Biltmore", "Camelback East", "Desert Ridge",
            "Ahwatukee", "Sunnyslope", "North Phoenix", "South Mountain", "Maryvale",
        ],
        "anchor_venues_es": "the Footprint Center, Chase Field, State Farm Stadium, the Phoenix Convention Center, Talking Stick Resort Arena",
        "regulatory_es": "Arizona sigue OSHA federal. El calor del verano (mayo a septiembre, hasta 115°F) requiere productos resistentes al calor y servicio dos veces por semana &mdash; lo incluimos sin cargo extra. Sombra y ventilación son críticas; nuestros conductores ayudan con la ubicación óptima.",
        "use_cases_es": [
            ("Construcción en el desierto", "Cumplimiento OSHA, servicios reforzados durante el verano para control de olor."),
            ("Eventos al aire libre", "Phoenix Open, festivales del valle, Spring Training &mdash; servicio nocturno y placement con sombra."),
            ("Bodas", "Tráileres de baños de lujo con aire acondicionado &mdash; esencial en el calor del verano."),
            ("Festivales y conciertos", "Servicio para festivales del valle, Innings Festival, conciertos en Talking Stick Resort."),
            ("Emergencias", "Respuesta 24 horas, fallas de plomería, refugios de emergencia."),
        ],
    },
]

TEMPLATE = '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Renta de Baños Portátiles {city}, {state} — Entrega el Mismo Día | FixPilot</title>
<meta name="description" content="Renta de baños portátiles en {city}, {state_full_es}. Entrega el mismo día, baños de lujo, accesibles ADA, estaciones de lavado, baños de construcción. Llame al (833) 652-9344 las 24 horas.">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<link rel="canonical" href="https://fixpilotportapottyrentals.com/es/{slug}">
<link rel="alternate" hreflang="es-US" href="https://fixpilotportapottyrentals.com/es/{slug}">
<link rel="alternate" hreflang="en-US" href="https://fixpilotportapottyrentals.com/{en_slug}">
<link rel="alternate" hreflang="x-default" href="https://fixpilotportapottyrentals.com/{en_slug}">
<meta name="geo.region" content="US-{state}">
<meta name="geo.placename" content="{city}, {state_full_es}">
<meta name="geo.position" content="{lat};{lon}">
<meta property="og:title" content="Renta de Baños Portátiles {city}, {state}">
<meta property="og:description" content="Entrega el mismo día. Baños de lujo, accesibles ADA, estaciones de lavado. (833) 652-9344.">
<meta property="og:url" content="https://fixpilotportapottyrentals.com/es/{slug}">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_US">
<meta property="og:locale:alternate" content="en_US">
<meta property="og:image" content="https://fixpilotportapottyrentals.com/hero-banner-images/1.%2020260226_225037_822.webp">

<link rel="stylesheet" href="/assets/tw.css">
<style>:root{{--brand-50:#eff6ff;--brand-100:#dbeafe;--brand-200:#bfdbfe;--brand-300:#93c5fd;--brand-400:#60a5fa;--brand-500:#3b82f6;--brand-600:#2563eb;--brand-700:#1d4ed8;--brand-800:#1e40af;--brand-900:#1e3a8a;--brand-950:#172554;--cta:#ea580c}}</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"LocalBusiness","name":"FixPilot Renta de Baños Portátiles — {city}","description":"Renta de baños portátiles en {city}, {state_full_es}. Entrega el mismo día. Servicio en español.","url":"https://fixpilotportapottyrentals.com/es/{slug}","inLanguage":"es-US","telephone":"+18336529344","address":{{"@type":"PostalAddress","addressLocality":"{city}","addressRegion":"{state}","postalCode":"{zip}","addressCountry":"US"}},"geo":{{"@type":"GeoCoordinates","latitude":{lat},"longitude":{lon}}},"areaServed":{{"@type":"City","name":"{city}"}}}}
</script>
</head>
<body class="bg-gray-50 text-gray-900">

<header class="bg-white shadow-md sticky top-0 z-40">
  <div class="container mx-auto px-4 py-4 flex items-center justify-between">
    <a href="/es" class="flex items-center gap-2"><div class="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center"><span class="text-white font-bold text-xl">F</span></div><span class="text-xl font-bold">FixPilot</span></a>
    <nav class="hidden md:flex items-center gap-6 text-sm font-bold">
      <a href="/es" class="hover:text-green-700">Inicio</a>
      <a href="/{en_slug}" class="hover:text-green-700"><i class="fas fa-globe mr-1"></i>English</a>
    </nav>
    <a href="tel:+18336529344" class="bg-green-600 text-white px-4 py-2 rounded-lg font-bold hover:bg-green-700"><i class="fas fa-phone mr-2"></i>(833) 652-9344</a>
  </div>
</header>

<aside class="bg-amber-50 border-l-4 border-amber-400 px-6 py-4 text-amber-900">
  <p class="text-sm md:text-base"><strong>¿Necesita un baño hoy?</strong> Llame al <a href="tel:+18336529344" class="font-bold underline">(833) 652-9344</a> &mdash; entrega el mismo día en {city} y todo el área metropolitana. Hablamos español.</p>
</aside>

<section class="bg-gradient-to-r from-green-700 to-green-900 text-white py-16 md:py-24">
  <div class="container mx-auto px-4 max-w-4xl text-center">
    <span class="inline-block bg-white/20 text-white text-xs font-bold uppercase tracking-widest px-4 py-1 rounded-full mb-4">Construcción &middot; Eventos &middot; Bodas &middot; Emergencias</span>
    <h1 class="text-4xl md:text-5xl font-extrabold mb-4 leading-tight">Renta de Baños Portátiles en {city}, {state}</h1>
    <p class="text-xl mb-8 text-green-100 max-w-3xl mx-auto">{intro_es}</p>
    <a href="tel:+18336529344" class="bg-white text-green-700 px-8 py-4 rounded-2xl font-extrabold text-2xl shadow-lg hover:bg-green-50 inline-flex items-center gap-2"><i class="fas fa-phone"></i> Llame al (833) 652-9344</a>
    <p class="mt-4 text-green-100 text-sm">Despacho 24 horas en español &middot; entrega el mismo día &middot; con licencia y seguro de $2M.</p>
  </div>
</section>

<main class="py-16">
  <div class="container mx-auto px-4 max-w-3xl">
    <h2 class="text-3xl md:text-4xl font-bold text-gray-800 mb-4">Tipos de baños portátiles que ofrecemos en {city}</h2>
    <ul class="space-y-3 mb-6">
      <li class="bg-white p-5 rounded-xl shadow border border-gray-200"><strong><a href="/services/standard-porta-potty" class="text-green-700 underline">Baño portátil estándar</a></strong> &mdash; el básico para construcción y eventos al aire libre. $50&ndash;$95/día.</li>
      <li class="bg-white p-5 rounded-xl shadow border border-gray-200"><strong><a href="/services/deluxe-porta-potty" class="text-green-700 underline">Baño portátil de lujo (deluxe)</a></strong> &mdash; con lavabo, agua corriente, espejo. $85&ndash;$145/día.</li>
      <li class="bg-white p-5 rounded-xl shadow border border-gray-200"><strong><a href="/services/luxury-restroom-trailers" class="text-green-700 underline">Tráiler de baños de lujo</a></strong> &mdash; con aire acondicionado, inodoros con descarga, agua caliente. Para bodas y eventos formales. $300&ndash;$1,200/día.</li>
      <li class="bg-white p-5 rounded-xl shadow border border-gray-200"><strong><a href="/services/ada-compliant-units" class="text-green-700 underline">Unidad ADA accesible</a></strong> &mdash; cumple con la Ley para Personas con Discapacidades. Requerida en eventos públicos.</li>
      <li class="bg-white p-5 rounded-xl shadow border border-gray-200"><strong><a href="/services/hand-wash-stations" class="text-green-700 underline">Estación de lavado de manos</a></strong> &mdash; con agua, jabón y toallas de papel.</li>
      <li class="bg-white p-5 rounded-xl shadow border border-gray-200"><strong><a href="/services/construction-porta-potty-rentals" class="text-green-700 underline">Baños de construcción</a></strong> &mdash; cumplen con OSHA 29 CFR 1926.51.</li>
    </ul>

    <h2 class="text-3xl md:text-4xl font-bold text-gray-800 mt-12 mb-4">Casos de uso comunes en {city}</h2>
    <ul class="space-y-3 mb-6">
{use_cases_html}
    </ul>

    <h2 class="text-3xl md:text-4xl font-bold text-gray-800 mt-12 mb-4">Vecindarios que servimos</h2>
    <p class="text-gray-700 leading-relaxed mb-4">Entregamos a todos los vecindarios y áreas metropolitanas de {city}, incluyendo:</p>
    <div class="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
{neighborhoods_html}
    </div>
    <p class="text-gray-700 leading-relaxed mb-4">Eventos importantes y lugares cerca: {anchor_venues_es}.</p>

    <h2 class="text-3xl md:text-4xl font-bold text-gray-800 mt-12 mb-4">Cumplimiento y regulaciones</h2>
    <p class="text-gray-700 leading-relaxed mb-4">{regulatory_es}</p>

    <h2 class="text-3xl md:text-4xl font-bold text-gray-800 mt-12 mb-4">Cómo funciona</h2>
    <ol class="list-decimal pl-6 space-y-2 text-gray-700 mb-6">
      <li><strong>Llame al (833) 652-9344</strong> &mdash; nuestro despachador habla español</li>
      <li><strong>Cotización en 60 segundos</strong> &mdash; le damos el precio total, sin sorpresas en la factura</li>
      <li><strong>Confirmación inmediata</strong> &mdash; recibe el certificado de seguro (COI) por correo en 60 minutos</li>
      <li><strong>Entrega el mismo día</strong> &mdash; en la mayoría de las ciudades, si pide antes del mediodía</li>
      <li><strong>Servicio durante el alquiler</strong> &mdash; semanal o más frecuente según el uso</li>
      <li><strong>Recogida</strong> &mdash; cuando termine el evento o proyecto</li>
    </ol>

    <aside class="bg-green-50 border-l-4 border-green-700 p-6 rounded-r-lg my-10 text-center">
      <h3 class="font-extrabold text-2xl text-gray-900 mb-2">Cotización en 60 segundos</h3>
      <p class="text-gray-700 mb-4">Sin formularios. Hable directamente con nuestro despachador en español.</p>
      <a href="tel:+18336529344" class="inline-block bg-green-600 hover:bg-green-700 text-white font-extrabold text-2xl py-4 px-8 rounded-2xl shadow-lg pulse-btn"><i class="fas fa-phone mr-2"></i>(833) 652-9344</a>
    </aside>

    <p class="text-gray-700 leading-relaxed mt-8">Para más detalles en inglés (precios, calculadora de unidades, blog), visite nuestra <a href="/{en_slug}" class="text-green-700 font-bold underline">página de {city} en inglés</a>.</p>
  </div>
</main>

<footer class="bg-gray-900 text-gray-300 py-12"><div class="container mx-auto px-4 text-center text-sm"><p class="mb-2">&copy; FixPilot Porta Potty Rentals &mdash; 224 ciudades, 50 estados, despacho 24 horas.</p><p><a href="tel:+18336529344" class="text-green-400 font-bold">(833) 652-9344</a> &middot; <a href="/locations" class="hover:underline">Áreas de servicio</a> &middot; <a href="/{en_slug}" class="hover:underline">English</a></p></div></footer>

<div id="mobile-cta" class="fixed bottom-0 left-0 right-0 bg-green-600 shadow-2xl transform translate-y-full transition-transform duration-300 z-50 md:hidden flex items-stretch" style="z-index: 9999;"><a href="tel:+18336529344" class="flex-1 py-4 text-center text-white font-extrabold text-lg"><i class="fas fa-phone-alt mr-2 animate-pulse"></i>Llame al (833) 652-9344</a><button id="mobile-cta-dismiss" type="button" aria-label="Ocultar botón" class="px-4 text-white/80 hover:text-white text-2xl leading-none">&times;</button></div>
<script>(function(){{var c=document.getElementById('mobile-cta'),d=document.getElementById('mobile-cta-dismiss');if(!c)return;var x=false;try{{x=sessionStorage.getItem('mobileCtaDismissed')==='1';}}catch(e){{}}if(x){{c.style.display='none';return;}}window.addEventListener('scroll',function(){{if(x)return;c.style.transform=window.scrollY>300?'translateY(0)':'translateY(100%)';}},{{passive:true}});if(d){{d.addEventListener('click',function(e){{e.preventDefault();x=true;c.style.transform='translateY(100%)';setTimeout(function(){{c.style.display='none';}},300);try{{sessionStorage.setItem('mobileCtaDismissed','1');}}catch(e){{}}}});}}}})();</script>
</body>
</html>
'''


def main() -> None:
    written = 0
    for c in CITIES:
        folder = f"es/{c['slug']}"
        os.makedirs(folder, exist_ok=True)
        out = f"{folder}/index.html"
        if os.path.exists(out):
            print(f"  exists: {out}")
            continue

        use_cases_html = "\n".join(
            f'      <li class="bg-white p-5 rounded-xl shadow border border-gray-200"><strong>{title}</strong> &mdash; {desc}</li>'
            for title, desc in c["use_cases_es"]
        )

        neighborhoods_html = "\n".join(
            f'      <span class="bg-white p-3 rounded-lg shadow text-center font-bold">{n}</span>'
            for n in c["neighborhoods_es"]
        )

        html = TEMPLATE.format(
            slug=c["slug"],
            en_slug=c["en_slug"],
            city=c["city"],
            state=c["state"],
            state_full_es=c["state_full_es"],
            lat=c["lat"],
            lon=c["lon"],
            zip=c["zip"],
            intro_es=c["intro_es"],
            use_cases_html=use_cases_html,
            neighborhoods_html=neighborhoods_html,
            anchor_venues_es=c["anchor_venues_es"],
            regulatory_es=c["regulatory_es"],
        )
        open(out, "w", encoding="utf-8").write(html)
        print(f"  wrote: {out}")
        written += 1

    print(f"\nWrote {written} Spanish city pages.")


if __name__ == "__main__":
    main()
