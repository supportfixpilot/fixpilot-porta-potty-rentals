"""Restore corrupted files and re-apply service links correctly.
Processes replacements in reverse order to avoid offset shifting."""
import re
import os

BASE = "/Users/hasanulrubel/Playground/PPC/porta-potty-rental"

# ============================================================
# ORIGINAL service sections extracted from initial file reads
# Key = filename (relative to BASE), Value = original section text
# ============================================================

ORIGINAL_SECTIONS = {}

# ---------- Arlington ----------
ORIGINAL_SECTIONS["porta-potty-rental-arlington-tx/index.html"] = r"""<section id="services" class="py-20 bg-brand-50">
  <div class="container mx-auto px-4">
    <div class="text-center mb-16 max-w-4xl mx-auto">
      <h2 class="text-4xl md:text-5xl font-black text-brand-950 mb-6 tracking-tight uppercase">Complete Portable Sanitation Services in Arlington, TX</h2>
      <p class="text-brand-800 leading-relaxed text-lg font-medium">
        From navigating tailgate lots near AT&T Stadium to servicing sprawling commercial developments in East Arlington, we provide the most reliable porta potty rentals in Tarrant County. We offer end-to-end sanitation solutions tailored to the extreme demands of the Texas climate.
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
      
      <div class="sharp-card bg-white flex flex-col relative">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/construction-porta-potty-rentals/14. 20260226_140515_190.webp" width="400" height="250" alt="Construction Porta Potty Rentals Arlington TX" class="w-full h-56 object-cover">
            <div class="absolute top-4 right-4 bg-brand-900 text-white text-xs font-black uppercase px-3 py-1 border border-brand-700">High Demand</div>
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Construction Porta Potties</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-medium">Keep your DFW job site compliant, productive, and clean. Our rugged construction units are built to withstand heavy use and the intense Texas sun. Delivered promptly anywhere from residential builds in Pantego to major commercial developments along I-20, backed by our rock-solid weekly servicing schedule.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="sharp-card bg-white flex flex-col relative">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/luxary-restroom-trailers/4. 20260226_141636_108.webp" width="400" height="250" alt="Luxury Restroom Trailer Rentals Arlington TX" class="w-full h-56 object-cover">
            <div class="absolute top-4 right-4 bg-cta text-white text-xs font-black uppercase px-3 py-1">Premium AC</div>
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Luxury Restroom Trailers</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-medium">Elevate your high-end Arlington wedding, corporate retreat, or VIP event in Viridian. These climate-controlled mobile restrooms mimic the interior of an upscale hotel. Featuring flushing porcelain toilets, running hot and cold water, vanity mirrors, and powerful AC to beat the Texas heat.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="sharp-card bg-white flex flex-col relative">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/standard-porta-potty/13. 20260226_145347_591.webp" width="400" height="250" alt="Standard Porta Potty Rental Arlington TX" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Standard Porta Potties</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-medium">The backbone of portable sanitation. Our standard units are a highly cost-effective and reliable choice for casual outdoor events, block parties in Dalworthington Gardens, and short-term home remodeling projects. They feature excellent ventilation, anti-slip flooring, and are delivered impeccably clean.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="sharp-card bg-white flex flex-col relative">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/ada-compliant-units/9. 20260226_142858_542.webp" width="400" height="250" alt="ADA Compliant Portable Toilets Arlington TX" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">ADA-Compliant Units</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-medium">Ensure your public Arlington festival or commercial site meets all accessibility requirements and Texas building codes. These oversized, wheelchair-friendly porta potties feature a true ground-level entrance, a spacious interior for full turnaround capability, and heavy-duty reinforced grab bars.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="sharp-card bg-white flex flex-col relative">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/handwash-stations/6. 20260226_151824_035.webp" width="400" height="250" alt="Hand Wash Station Rentals Arlington TX" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Hand Wash Stations</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-medium">Promote top-tier hygiene and meet stringent Tarrant County health regulations. Our standalone, multi-user handwashing stations are operated via a hands-free foot pump. Delivered fully stocked with fresh water, antibacterial soap, and paper towels—perfect for food truck rallies near UT Arlington.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="sharp-card bg-white flex flex-col relative">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/flushable-portable-toilets/9. 20260226_185840_732.webp" width="400" height="250" alt="Flushable Portable Toilets Arlington TX" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Flushable Portable Toilets</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-medium">A fantastic upgrade from the standard drop-tank design. These VIP single units hide the waste from view using a fresh-water foot-pump flush mechanism. Combined with an integrated sink and mirror, they offer a significantly more pleasant experience for upscale backyard gatherings.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="sharp-card bg-white flex flex-col relative">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/event-restroom-trailers/15. 20260226_153059_541.webp" width="400" height="250" alt="Event Restroom Trailers Arlington TX" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Event Restroom Trailers</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-medium">When hosting hundreds of people at a concert, tailgating lot, or sporting event in the Entertainment District, managing crowd flow is critical. Our high-capacity event restroom trailers feature multiple private stalls and sinks, drastically reducing wait times while maintaining pristine conditions.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="sharp-card bg-white flex flex-col relative">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/crane-hook-toilets-for-rental/4. 20260226_193514_723.webp" width="400" height="250" alt="Crane Hook Porta Potty Arlington TX" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Crane Hook Units</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-medium">Designed specifically for multi-story commercial developments in Downtown Arlington. These units feature integrated, heavy-duty steel slings allowing your crane operator to safely hoist sanitation directly to elevated floors, saving time and maximizing site efficiency.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="sharp-card bg-white flex flex-col relative">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/vip-trailers-rental/5. 20260226_160618_188.webp" width="400" height="250" alt="VIP Trailer Rentals Arlington TX" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">VIP Trailer Rentals</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-medium">The pinnacle of portable sanitation. Specifically requested for exclusive outdoor galas, corporate sponsor tents, and VIP areas. These ultra-luxury trailers feature wood-grain flooring, custom cabinetry, premium sound systems, and porcelain fixtures.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="sharp-card bg-white flex flex-col relative">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/deluxe-porta-potty/8. 20260226_150048_652.webp" width="400" height="250" alt="Deluxe Porta Potty Rentals Arlington TX" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Deluxe Porta Potties</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-medium">Offering a roomier interior footprint than standard units, our deluxe porta potties are designed with user comfort in mind. They come equipped with thoughtful additions like a convenience shelf, a coat hook, and a small mirror. An excellent upgrade for weekend parties in North Arlington.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="sharp-card bg-white flex flex-col relative">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/septic-pumping-and-holding-tanks-optimized/12. 20260226_143837_364.webp" width="400" height="250" alt="Septic Pumping Holding Tanks Arlington TX" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Holding Tanks & Pumping</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-medium">For long-term construction compounds or remote office trailers that lack direct sewer line access, we supply heavy-duty holding tanks. Our fleet of vacuum trucks also provides rapid, scheduled septic pumping services to prevent overflows across Tarrant County.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="sharp-card bg-white flex flex-col relative">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/emergency -Short-Term Rentals/8. 20260301_223123_300.webp" width="400" height="250" alt="Emergency Porta Potty Rentals Arlington TX" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Emergency / Disaster Relief</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-medium">When unexpected plumbing failures or severe Texas weather strikes, rapid response is crucial. Our emergency dispatch team is available 24/7 to deploy portable toilets and hand wash stations to affected neighborhoods across DFW.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

    </div>
  </div>
</section>"""

# ---------- Frederick ----------
ORIGINAL_SECTIONS["porta-potty-rental-frederick-md/index.html"] = r"""<section id="services" class="py-20 bg-white">
  <div class="container mx-auto px-4">
    <div class="text-center mb-16">
      <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Complete Portable Sanitation Services in Frederick, MD</h2>
      <p class="text-gray-600 mb-6 leading-relaxed max-w-3xl mx-auto">
        Whether you need a single unit for a backyard party in Tasker's Chance or fifty units for a street festival in Downtown Frederick, we have the inventory and expertise to handle it flawlessly.
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition">
        <img loading="lazy" src="../service-images/construction-porta-potty-rentals/9. 20260226_135951_178.webp" width="352" height="192" alt="Construction Porta Potty Rentals Frederick CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2 text-gray-900">Construction Porta Potty Rentals</h3>
          <p class="text-gray-600 text-sm mb-3">Durable, heavy-duty units ideal for Frederick job sites. Includes reliable weekly cleaning and restocking to keep your crews productive.</p>
        </div>
        <div class="px-5 pb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition">
        <img loading="lazy" src="../service-images/luxary-restroom-trailers/10. 20260226_141432_821.webp" width="352" height="192" alt="Luxury Restroom Trailers Frederick CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2 text-gray-900">Luxury Restroom Trailers</h3>
          <p class="text-gray-600 text-sm mb-3">Elevate your upscale Frederick wedding or corporate event with climate-controlled trailers featuring flushing toilets, mirrors, and running water.</p>
        </div>
        <div class="px-5 pb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition">
        <img loading="lazy" src="../service-images/ada-compliant-units/18. 20260226_143014_440.webp" width="352" height="192" alt="ADA-Compliant Units Frederick CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2 text-gray-900">ADA-Compliant Units</h3>
          <p class="text-gray-600 text-sm mb-3">Ensure your Frederick public event is accessible to everyone. These spacious units feature ground-level access and sturdy grab bars.</p>
        </div>
        <div class="px-5 pb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition">
        <img loading="lazy" src="../service-images/standard-porta-potty/4. 20260226_145210_936.webp" width="352" height="192" alt="Standard Porta Potty CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2 text-gray-900">Standard Porta Potty</h3>
          <p class="text-gray-600 text-sm mb-3">The cost-effective backbone for backyard parties, parks, and short-term projects across Frederick. Clean, well-ventilated, and fully stocked.</p>
        </div>
        <div class="px-5 pb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition">
         <img loading="lazy" src="../service-images/handwash-stations/8. 20260226_151409_569.webp" width="352" height="192" alt="Hand Wash Stations CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2 text-gray-900">Hand Wash Stations</h3>
          <p class="text-gray-600 text-sm mb-3">Keep guests and workers healthy. Our foot-pump sinks come fully loaded with fresh water, soap, and paper towels for any Frederick location.</p>
        </div>
        <div class="px-5 pb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition">
        <img loading="lazy" src="../service-images/event-restroom-trailers/20. 20260226_153133_541.webp" width="352" height="192" alt="Event Restroom Trailers CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2 text-gray-900">Event Restroom Trailers</h3>
          <p class="text-gray-600 text-sm mb-3">Handling large crowds for a Frederick festival? Multi-stall event trailers provide high-volume capacity without sacrificing cleanliness or comfort.</p>
        </div>
        <div class="px-5 pb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition">
         <img loading="lazy" src="../service-images/flushable-portable-toilets/10. 20260226_190227_095.webp" width="352" height="192" alt="Flushable Portable Toilets CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2 text-gray-900">Flushable Portable Toilets</h3>
          <p class="text-gray-600 text-sm mb-3">A premium upgrade from standard units. These feature a hidden waste tank and foot-pump flushing mechanism, popular for Frederick corporate retreats.</p>
        </div>
        <div class="px-5 pb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition">
         <img loading="lazy" src="../service-images/septic-pumping-and-holding-tanks-optimized/13. 20260226_143851_540.webp" width="352" height="192" alt="Septic Pumping & Holding Tanks CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2 text-gray-900">Septic Pumping & Holding Tanks</h3>
          <p class="text-gray-600 text-sm mb-3">We supply large capacity holding tanks for remote Frederick construction trailers and provide rapid, reliable septic pumping services.</p>
        </div>
        <div class="px-5 pb-5 mt-auto">
          Get a Quote
        </div>
      </div>
      
      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition">
         <img loading="lazy" src="../service-images/rolling-porta-potty-for-rent-optimized/18. 20260226_192629_936.webp" width="352" height="192" alt="Crane Hook Porta Potty CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2 text-gray-900">Crane Hook Porta Potty</h3>
          <p class="text-gray-600 text-sm mb-3">Essential for high-rise or multi-level commercial builds in Frederick. Specially designed slings allow safe lifting to upper elevations.</p>
        </div>
        <div class="px-5 pb-5 mt-auto">
          Get a Quote
        </div>
      </div>
      
      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition">
         <img loading="lazy" src="../service-images/emergency -Short-Term Rentals/13. 20260301_225608_556.webp" width="352" height="192" alt="Emergency & Short-Term CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2 text-gray-900">Emergency & Short-Term</h3>
          <p class="text-gray-600 text-sm mb-3">Facing plumbing failures or disaster recovery in Frederick County? We provide rapid deployment of emergency sanitation resources 24/7.</p>
        </div>
        <div class="px-5 pb-5 mt-auto">
          Get a Quote
        </div>
      </div>
      
      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition">
         <img loading="lazy" src="../service-images/porta-potty-on Trailer – Trailer Mounted Porta Potty Rentals/11. 20260226_223059_736.webp" width="352" height="192" alt="Trailer Mounted Rentals CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2 text-gray-900">Trailer Mounted Rentals</h3>
          <p class="text-gray-600 text-sm mb-3">Ideal for road crews and agricultural workers moving across Frederick County. Highly mobile units mounted on street-legal trailers.</p>
        </div>
        <div class="px-5 pb-5 mt-auto">
          Get a Quote
        </div>
      </div>
      
      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition">
         <img loading="lazy" src="../service-images/restroom-trailers-setup-and-removal-optimized/17. 20260226_161648_776.webp" width="352" height="192" alt="Hand Sanitizer Stands CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2 text-gray-900">Hand Sanitizer Stands</h3>
          <p class="text-gray-600 text-sm mb-3">Compact, free-standing sanitizer towers. A perfect low-cost addition to entryways, food zones, and ticket booths at Frederick events.</p>
        </div>
        <div class="px-5 pb-5 mt-auto">
          Get a Quote
        </div>
      </div>

    </div>
  </div>
</section>"""

# ---------- Glendale ----------
ORIGINAL_SECTIONS["porta-potty-rental-glendale-ca/index.html"] = r"""<section id="services" class="py-24 bg-white">
  <div class="container mx-auto px-4">
    <div class="text-center mb-16 max-w-4xl mx-auto">
      <h2 class="text-4xl md:text-5xl font-black text-brand-950 mb-6 tracking-tight">Complete Portable Sanitation Services in Glendale, CA</h2>
      <p class="text-brand-700 leading-relaxed text-lg font-medium">
        From navigating hillside properties in Chevy Chase Canyon to servicing sprawling commercial developments in Downtown Glendale, we provide the most reliable porta potty rentals in Los Angeles County. 
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-10">
      
      <div class="flex flex-col bg-white rounded-3xl shadow-lg border-2 border-brand-100 overflow-hidden hover:shadow-offset-hover hover:-translate-y-2 transition-all duration-300">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/construction-porta-potty-rentals/1. 20260226_124452_973.webp" width="400" height="250" alt="Construction Porta Potty Rentals Glendale CA" class="w-full h-56 object-cover">
            <div class="absolute top-4 right-4 bg-brand-900 text-white text-xs font-black uppercase px-4 py-2 rounded-full shadow-md">High Demand</div>
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Construction Porta Potties</h3>
          <p class="text-brand-600 text-sm mb-4 leading-relaxed font-medium">Keep your LA County job site compliant, productive, and clean. Our rugged construction units are built to withstand heavy use. Delivered promptly anywhere from Adams Hill residential builds to major downtown commercial developments, backed by our weekly servicing schedule.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-3xl shadow-lg border-2 border-brand-100 overflow-hidden hover:shadow-offset-hover hover:-translate-y-2 transition-all duration-300">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/luxary-restroom-trailers/7. 20260226_142021_592.webp" width="400" height="250" alt="Luxury Restroom Trailer Rentals Glendale CA" class="w-full h-56 object-cover">
            <div class="absolute top-4 right-4 bg-cta text-white text-xs font-black uppercase px-4 py-2 rounded-full shadow-md">Premium</div>
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Luxury Restroom Trailers</h3>
          <p class="text-brand-600 text-sm mb-4 leading-relaxed font-medium">Elevate your high-end Glendale wedding, corporate retreat, or VIP event. These climate-controlled mobile restrooms mimic the interior of an upscale hotel. Featuring flushing porcelain toilets, running hot and cold water, vanity mirrors, and powerful AC to beat the California heat.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-3xl shadow-lg border-2 border-brand-100 overflow-hidden hover:shadow-offset-hover hover:-translate-y-2 transition-all duration-300">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/standard-porta-potty/3. 20260226_145200_803.webp" width="400" height="250" alt="Standard Porta Potty Rental Glendale CA" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Standard Porta Potties</h3>
          <p class="text-brand-600 text-sm mb-4 leading-relaxed font-medium">The backbone of portable sanitation. Our standard units are a highly cost-effective and reliable choice for casual outdoor events, block parties in Montrose, and short-term home remodeling projects. They feature excellent ventilation, anti-slip flooring, and are delivered impeccably clean.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-3xl shadow-lg border-2 border-brand-100 overflow-hidden hover:shadow-offset-hover hover:-translate-y-2 transition-all duration-300">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/ada-compliant-units/5. 20260226_142530_947.webp" width="400" height="250" alt="ADA Compliant Portable Toilets Glendale CA" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">ADA-Compliant Units</h3>
          <p class="text-brand-600 text-sm mb-4 leading-relaxed font-medium">Ensure your public Glendale event or commercial site meets all accessibility requirements and California building codes. These oversized, wheelchair-friendly porta potties feature a true ground-level entrance, a spacious interior for full turnaround capability, and heavy-duty reinforced grab bars.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-3xl shadow-lg border-2 border-brand-100 overflow-hidden hover:shadow-offset-hover hover:-translate-y-2 transition-all duration-300">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/handwash-stations/13. 20260226_151421_585.webp" width="400" height="250" alt="Hand Wash Station Rentals Glendale CA" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Hand Wash Stations</h3>
          <p class="text-brand-600 text-sm mb-4 leading-relaxed font-medium">Promote top-tier hygiene and meet stringent LA County Department of Public Health regulations. Our standalone, multi-user handwashing stations are operated via a hands-free foot pump. Delivered fully stocked with fresh water, antibacterial soap, and paper towels—perfect for food trucks or busy job sites.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-3xl shadow-lg border-2 border-brand-100 overflow-hidden hover:shadow-offset-hover hover:-translate-y-2 transition-all duration-300">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/flushable-portable-toilets/9. 20260226_190953_562.webp" width="400" height="250" alt="Flushable Portable Toilets Glendale CA" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Flushable Portable Toilets</h3>
          <p class="text-brand-600 text-sm mb-4 leading-relaxed font-medium">A fantastic upgrade from the standard drop-tank design. These VIP single units hide the waste from view using a fresh-water foot-pump flush mechanism. Combined with an integrated sink and mirror, they offer a significantly more pleasant experience for upscale gatherings in SoCal.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-3xl shadow-lg border-2 border-brand-100 overflow-hidden hover:shadow-offset-hover hover:-translate-y-2 transition-all duration-300">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/event-restroom-trailers/istockphoto-1397088600-612x612.webp" width="400" height="250" alt="Event Restroom Trailers Glendale CA" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Event Restroom Trailers</h3>
          <p class="text-brand-600 text-sm mb-4 leading-relaxed font-medium">When hosting hundreds of people at an outdoor concert, festival, or sporting event in Glendale, managing crowd flow is critical. Our high-capacity event restroom trailers feature multiple private stalls and sinks, drastically reducing wait times while maintaining pristine conditions.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-3xl shadow-lg border-2 border-brand-100 overflow-hidden hover:shadow-offset-hover hover:-translate-y-2 transition-all duration-300">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/crane-hook-toilets-for-rental/18. 20260226_193718_733.webp" width="400" height="250" alt="Crane Hook Porta Potty Glendale CA" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Crane Hook Units</h3>
          <p class="text-brand-600 text-sm mb-4 leading-relaxed font-medium">Designed specifically for multi-story commercial developments in Downtown Glendale. These units feature integrated, heavy-duty steel slings allowing your crane operator to safely hoist sanitation directly to elevated floors, saving time and maximizing site efficiency.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-3xl shadow-lg border-2 border-brand-100 overflow-hidden hover:shadow-offset-hover hover:-translate-y-2 transition-all duration-300">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/vip-trailers-rental/10. 20260226_160622_245.webp" width="400" height="250" alt="VIP Trailer Rentals Glendale CA" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">VIP Trailer Rentals</h3>
          <p class="text-brand-600 text-sm mb-4 leading-relaxed font-medium">The pinnacle of portable sanitation. Specifically requested for exclusive outdoor galas, corporate events, and Hollywood production sets. These ultra-luxury trailers feature wood-grain flooring, custom cabinetry, premium sound systems, and porcelain fixtures.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-3xl shadow-lg border-2 border-brand-100 overflow-hidden hover:shadow-offset-hover hover:-translate-y-2 transition-all duration-300">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/deluxe-porta-potty/14. 20260226_150134_051.webp" width="400" height="250" alt="Deluxe Porta Potty Rentals Glendale CA" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Deluxe Porta Potties</h3>
          <p class="text-brand-600 text-sm mb-4 leading-relaxed font-medium">Offering a roomier interior footprint than standard units, our deluxe porta potties are designed with user comfort in mind. They come equipped with thoughtful additions like a convenience shelf, a coat hook, and a small mirror. An excellent upgrade for weekend parties in Rossmoyne.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-3xl shadow-lg border-2 border-brand-100 overflow-hidden hover:shadow-offset-hover hover:-translate-y-2 transition-all duration-300">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/septic-pumping-and-holding-tanks-optimized/15. 20260226_143909_316.webp" width="400" height="250" alt="Septic Pumping Holding Tanks Glendale CA" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Holding Tanks & Pumping</h3>
          <p class="text-brand-600 text-sm mb-4 leading-relaxed font-medium">For long-term construction compounds or remote office trailers that lack direct sewer line access, we supply heavy-duty holding tanks. Our fleet of vacuum trucks also provides rapid, scheduled septic pumping services to prevent overflows in LA County.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-3xl shadow-lg border-2 border-brand-100 overflow-hidden hover:shadow-offset-hover hover:-translate-y-2 transition-all duration-300">
        <div class="relative overflow-hidden">
            <img loading="lazy" src="../service-images/emergency -Short-Term Rentals/9. 20260301_225101_565.webp" width="400" height="250" alt="Emergency Porta Potty Rentals Glendale CA" class="w-full h-56 object-cover">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight">Emergency / Disaster Relief</h3>
          <p class="text-brand-600 text-sm mb-4 leading-relaxed font-medium">When unexpected plumbing failures or severe weather events strike Southern California, rapid response is crucial. Our emergency dispatch team is available 24/7 to deploy portable toilets and hand wash stations to affected neighborhoods across Glendale and Burbank.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

    </div>
  </div>
</section>"""

# ---------- Mesa ----------
ORIGINAL_SECTIONS["porta-potty-rental-mesa-az/index.html"] = r"""<section id="services" class="py-24 bg-brand-50 border-b-8 border-brand-950">
  <div class="container mx-auto px-4">
    <div class="text-center mb-16 max-w-4xl mx-auto">
      <h2 class="text-4xl md:text-5xl font-black text-brand-950 mb-6 tracking-tight uppercase">Portable Sanitation Fleet in Mesa, AZ</h2>
      <p class="text-brand-800 leading-relaxed text-lg font-medium">
        From navigating master-planned communities in Eastmark to servicing sprawling commercial developments in the East Valley, we provide the most reliable porta potty rentals in Mesa. We offer end-to-end sanitation solutions tailored to the extreme Arizona desert environment.
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
      
      <div class="flex flex-col bg-white border-4 border-brand-950 shadow-brutal overflow-hidden transition-all duration-300 hover:-translate-y-2 group">
        <div class="relative overflow-hidden border-b-4 border-brand-950">
            <img loading="lazy" src="../service-images/construction-porta-potty-rentals/3. 20260226_135913_274.webp" width="400" height="250" alt="Construction Porta Potty Rentals Mesa AZ" class="w-full h-56 object-cover group-hover:scale-105 transition duration-500">
            <div class="absolute top-4 right-4 bg-cta text-white text-xs font-black uppercase px-3 py-1 shadow-md border-2 border-brand-950">High Demand</div>
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight uppercase">Construction Toilets</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-semibold">Keep your Maricopa County job site compliant, productive, and clean. Our rugged construction units are built to withstand heavy use and the intense Arizona sun. Delivered promptly anywhere from residential builds to major East Valley developments, backed by our rock-solid weekly servicing schedule.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white border-4 border-brand-950 shadow-brutal overflow-hidden transition-all duration-300 hover:-translate-y-2 group">
        <div class="relative overflow-hidden border-b-4 border-brand-950">
            <img loading="lazy" src="../service-images/luxary-restroom-trailers/6. 20260226_142021_530.webp" width="400" height="250" alt="Luxury Restroom Trailer Rentals Mesa AZ" class="w-full h-56 object-cover group-hover:scale-105 transition duration-500">
            <div class="absolute top-4 right-4 bg-brand-950 text-white text-xs font-black uppercase px-3 py-1 shadow-md border-2 border-white">Premium</div>
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight uppercase">Luxury Restroom Trailers</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-semibold">Elevate your high-end Mesa wedding, corporate retreat, or VIP event. These climate-controlled mobile restrooms mimic the interior of an upscale hotel. Featuring flushing porcelain toilets, running hot and cold water, vanity mirrors, and powerful AC to beat the desert heat.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white border-4 border-brand-950 shadow-brutal overflow-hidden transition-all duration-300 hover:-translate-y-2 group">
        <div class="relative overflow-hidden border-b-4 border-brand-950">
            <img loading="lazy" src="../service-images/standard-porta-potty/blue-portable-toilet.webp" width="400" height="250" alt="Standard Porta Potty Rental Mesa AZ" class="w-full h-56 object-cover group-hover:scale-105 transition duration-500">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight uppercase">Standard Porta Potties</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-semibold">The backbone of portable sanitation. Our standard units are a highly cost-effective and reliable choice for casual outdoor events, block parties in Dobson Ranch, and short-term home remodeling projects. They feature excellent ventilation, anti-slip flooring, and are delivered impeccably clean.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white border-4 border-brand-950 shadow-brutal overflow-hidden transition-all duration-300 hover:-translate-y-2 group">
        <div class="relative overflow-hidden border-b-4 border-brand-950">
            <img loading="lazy" src="../service-images/ada-compliant-units/15. 20260226_143253_670.webp" width="400" height="250" alt="ADA Compliant Portable Toilets Mesa AZ" class="w-full h-56 object-cover group-hover:scale-105 transition duration-500">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight uppercase">ADA-Compliant Units</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-semibold">Ensure your public Mesa event or commercial site meets all accessibility requirements and Arizona building codes. These oversized, wheelchair-friendly porta potties feature a true ground-level entrance, a spacious interior for full turnaround capability, and heavy-duty reinforced grab bars.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white border-4 border-brand-950 shadow-brutal overflow-hidden transition-all duration-300 hover:-translate-y-2 group">
        <div class="relative overflow-hidden border-b-4 border-brand-950">
            <img loading="lazy" src="../service-images/handwash-stations/14. 20260226_151423_582.webp" width="400" height="250" alt="Hand Wash Station Rentals Mesa AZ" class="w-full h-56 object-cover group-hover:scale-105 transition duration-500">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight uppercase">Hand Wash Stations</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-semibold">Promote top-tier hygiene and meet stringent Maricopa County Department of Health regulations. Our standalone, multi-user handwashing stations are operated via a hands-free foot pump. Delivered fully stocked with fresh water, antibacterial soap, and paper towels.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white border-4 border-brand-950 shadow-brutal overflow-hidden transition-all duration-300 hover:-translate-y-2 group">
        <div class="relative overflow-hidden border-b-4 border-brand-950">
            <img loading="lazy" src="../service-images/flushable-portable-toilets/16. 20260226_190257_041.webp" width="400" height="250" alt="Flushable Portable Toilets Mesa AZ" class="w-full h-56 object-cover group-hover:scale-105 transition duration-500">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight uppercase">Flushable Toilets</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-semibold">A fantastic upgrade from the standard drop-tank design. These VIP single units hide the waste from view using a fresh-water foot-pump flush mechanism. Combined with an integrated sink and mirror, they offer a significantly more pleasant experience for upscale desert gatherings.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white border-4 border-brand-950 shadow-brutal overflow-hidden transition-all duration-300 hover:-translate-y-2 group">
        <div class="relative overflow-hidden border-b-4 border-brand-950">
            <img loading="lazy" src="../service-images/event-restroom-trailers/istockphoto-1443289446-612x612.webp" width="400" height="250" alt="Event Restroom Trailers Mesa AZ" class="w-full h-56 object-cover group-hover:scale-105 transition duration-500">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight uppercase">Event Restroom Trailers</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-semibold">When hosting hundreds of people at a concert, spring training event, or sporting tournament in Mesa, managing crowd flow is critical. Our high-capacity event restroom trailers feature multiple private stalls and sinks, drastically reducing wait times.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white border-4 border-brand-950 shadow-brutal overflow-hidden transition-all duration-300 hover:-translate-y-2 group">
        <div class="relative overflow-hidden border-b-4 border-brand-950">
            <img loading="lazy" src="../service-images/crane-hook-toilets-for-rental/4. 20260226_193823_788.webp" width="400" height="250" alt="Crane Hook Porta Potty Mesa AZ" class="w-full h-56 object-cover group-hover:scale-105 transition duration-500">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight uppercase">Crane Hook Units</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-semibold">Designed specifically for multi-story commercial developments in the East Valley. These units feature integrated, heavy-duty steel slings allowing your crane operator to safely hoist sanitation directly to elevated floors, saving time and maximizing site efficiency.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white border-4 border-brand-950 shadow-brutal overflow-hidden transition-all duration-300 hover:-translate-y-2 group">
        <div class="relative overflow-hidden border-b-4 border-brand-950">
            <img loading="lazy" src="../service-images/vip-trailers-rental/15. 20260226_160628_193.webp" width="400" height="250" alt="VIP Trailer Rentals Mesa AZ" class="w-full h-56 object-cover group-hover:scale-105 transition duration-500">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight uppercase">VIP Trailer Rentals</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-semibold">The pinnacle of portable sanitation. Specifically requested for exclusive outdoor galas, corporate events, and VIP areas. These ultra-luxury trailers feature wood-grain flooring, custom cabinetry, premium sound systems, and porcelain fixtures.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white border-4 border-brand-950 shadow-brutal overflow-hidden transition-all duration-300 hover:-translate-y-2 group">
        <div class="relative overflow-hidden border-b-4 border-brand-950">
            <img loading="lazy" src="../service-images/deluxe-porta-potty/1. 20260226_150801_712.webp" width="400" height="250" alt="Deluxe Porta Potty Rentals Mesa AZ" class="w-full h-56 object-cover group-hover:scale-105 transition duration-500">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight uppercase">Deluxe Porta Potties</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-semibold">Offering a roomier interior footprint than standard units, our deluxe porta potties are designed with user comfort in mind. They come equipped with thoughtful additions like a convenience shelf, a coat hook, and a small mirror. An excellent upgrade for weekend parties.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white border-4 border-brand-950 shadow-brutal overflow-hidden transition-all duration-300 hover:-translate-y-2 group">
        <div class="relative overflow-hidden border-b-4 border-brand-950">
            <img loading="lazy" src="../service-images/septic-pumping-and-holding-tanks-optimized/4. 20260226_144141_718.webp" width="400" height="250" alt="Septic Pumping Holding Tanks Mesa AZ" class="w-full h-56 object-cover group-hover:scale-105 transition duration-500">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight uppercase">Holding Tanks & Pumping</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-semibold">For long-term construction compounds or remote office trailers that lack direct sewer line access, we supply heavy-duty holding tanks. Our fleet of vacuum trucks also provides rapid, scheduled septic pumping services to prevent overflows in Maricopa County.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white border-4 border-brand-950 shadow-brutal overflow-hidden transition-all duration-300 hover:-translate-y-2 group">
        <div class="relative overflow-hidden border-b-4 border-brand-950">
            <img loading="lazy" src="../service-images/emergency -Short-Term Rentals/15. 20260301_222616_518.webp" width="400" height="250" alt="Emergency Porta Potty Rentals Mesa AZ" class="w-full h-56 object-cover group-hover:scale-105 transition duration-500">
        </div>
        <div class="p-8 flex-grow">
          <h3 class="text-2xl font-black text-brand-950 mb-3 tracking-tight uppercase">Emergency Relief</h3>
          <p class="text-brand-700 text-sm mb-4 leading-relaxed font-semibold">When unexpected plumbing failures or severe desert microbursts strike, rapid response is crucial. Our emergency dispatch team is available 24/7 to deploy portable toilets and hand wash stations to affected neighborhoods across Mesa and the East Valley.</p>
        </div>
        <div class="px-8 pb-8 mt-auto">
          Get a Quote
        </div>
      </div>

    </div>
  </div>
</section>"""

# ---------- Naperville ----------
ORIGINAL_SECTIONS["porta-potty-rental-naperville-il/index.html"] = r"""<section id="services" class="py-20 bg-gray-50">
  <div class="container mx-auto px-4">
    <div class="text-center mb-16">
      <h2 class="text-3xl md:text-4xl font-extrabold text-gray-900 mb-4">Complete Portable Sanitation Services in Naperville, IL</h2>
      <p class="text-gray-600 text-lg leading-relaxed max-w-3xl mx-auto">
        Whether you're breaking ground on a new subdivision in <strong>South Naperville</strong> or hosting a beautiful outdoor reception near the <strong>Riverwalk</strong>, we offer the exact portable toilet rental you need.
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/construction-porta-potty-rentals/19. 20260226_140549_188.webp" width="352" height="192" alt="Construction Porta Potty Rentals Naperville CA" class="w-full h-48 object-cover">
        <div class="p-6 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Construction Porta Potty Rentals</h3>
          <p class="text-gray-600 text-sm mb-4">Rugged, weather-resistant units built for active Naperville job sites. Includes dependable weekly servicing to keep your crews productive and OSHA compliant.</p>
        </div>
        <div class="px-6 pb-6 text-center">
          <a href="tel:+18336529344" class="phone-link bg-cta text-white w-full py-3 rounded-xl font-bold inline-block hover:bg-orange-700 transition">Get a Quote</a>
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/standard-porta-potty/7. 20260226_145714_382.webp" width="352" height="192" alt="Standard Porta Potty Naperville IL" class="w-full h-48 object-cover">
        <div class="p-6 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Standard Porta Potty</h3>
          <p class="text-gray-600 text-sm mb-4">The go-to solution for backyard parties, 5K races, and short-term residential projects across Naperville. Clean, well-ventilated, and strictly sanitized.</p>
        </div>
        <div class="px-6 pb-6 text-center">
          <a href="tel:+18336529344" class="phone-link bg-cta text-white w-full py-3 rounded-xl font-bold inline-block hover:bg-orange-700 transition">Get a Quote</a>
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/ada-compliant-units/15. 20260226_142654_823.webp" width="352" height="192" alt="ADA Compliant Portable Toilets Naperville" class="w-full h-48 object-cover">
        <div class="p-6 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">ADA-Compliant Units</h3>
          <p class="text-gray-600 text-sm mb-4">Extra-wide doors, ground-level access, and sturdy interior grab bars. These wheelchair-accessible units ensure inclusive sanitation for all Naperville events.</p>
        </div>
        <div class="px-6 pb-6 text-center">
          <a href="tel:+18336529344" class="phone-link bg-cta text-white w-full py-3 rounded-xl font-bold inline-block hover:bg-orange-700 transition">Get a Quote</a>
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/luxary-restroom-trailers/5. 20260226_141654_109.webp" width="352" height="192" alt="Luxury Restroom Trailers Naperville" class="w-full h-48 object-cover">
        <div class="p-6 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Luxury Restroom Trailers</h3>
          <p class="text-gray-600 text-sm mb-4">Elevate your DuPage County wedding or VIP corporate event. Features real flushing toilets, running water, vanity mirrors, and premium climate control.</p>
        </div>
        <div class="px-6 pb-6 text-center">
          <a href="tel:+18336529344" class="phone-link bg-cta text-white w-full py-3 rounded-xl font-bold inline-block hover:bg-orange-700 transition">Get a Quote</a>
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/restroom-trailers-setup-and-removal-optimized/2. 20260226_161436_840.webp" width="352" height="192" alt="Hand Wash Stations Naperville IL" class="w-full h-48 object-cover">
        <div class="p-6 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Hand Wash & Sanitizer Stations</h3>
          <p class="text-gray-600 text-sm mb-4">Keep crowds healthy at Naperville festivals or construction zones. Standalone dual-sink stations stocked with fresh water, anti-bacterial soap, and towels.</p>
        </div>
        <div class="px-6 pb-6 text-center">
          <a href="tel:+18336529344" class="phone-link bg-cta text-white w-full py-3 rounded-xl font-bold inline-block hover:bg-orange-700 transition">Get a Quote</a>
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/fancy-portable-restroom-trailers-for-rent/8. 20260226_223047_796.webp" width="352" height="192" alt="Event Portable Restrooms Naperville" class="w-full h-48 object-cover">
        <div class="p-6 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Flushable Portable Toilets</h3>
          <p class="text-gray-600 text-sm mb-4">A step up from standard units, offering a foot-pump operated flushing mechanism to hide waste, reducing odors for upscale Naperville gatherings.</p>
        </div>
        <div class="px-6 pb-6 text-center">
          <a href="tel:+18336529344" class="phone-link bg-cta text-white w-full py-3 rounded-xl font-bold inline-block hover:bg-orange-700 transition">Get a Quote</a>
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/construction-porta-potty-rentals/18. 20260226_140549_123.webp" width="352" height="192" alt="Emergency Porta Potty Rentals Naperville" class="w-full h-48 object-cover">
        <div class="p-6 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Emergency / Disaster Rentals</h3>
          <p class="text-gray-600 text-sm mb-4">When water mains break or severe weather strikes Illinois, our rapid response team provides emergency sanitation support 24/7 across Naperville.</p>
        </div>
        <div class="px-6 pb-6 text-center">
          <a href="tel:+18336529344" class="phone-link bg-cta text-white w-full py-3 rounded-xl font-bold inline-block hover:bg-orange-700 transition">Get a Quote</a>
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/rolling-porta-potty-for-rent-optimized/6. 20260226_192451_688.webp" width="352" height="192" alt="Rolling Porta Potty Naperville IL" class="w-full h-48 object-cover">
        <div class="p-6 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Rolling & Crane-Hook Units</h3>
          <p class="text-gray-600 text-sm mb-4">Designed specifically for high-rise developments or tricky municipal projects. Easily maneuvered into tight spaces or hoisted by crane onto upper floors.</p>
        </div>
        <div class="px-6 pb-6 text-center">
          <a href="tel:+18336529344" class="phone-link bg-cta text-white w-full py-3 rounded-xl font-bold inline-block hover:bg-orange-700 transition">Get a Quote</a>
        </div>
      </div>
    </div>
  </div>
</section>"""

# ---------- Oakland ----------
ORIGINAL_SECTIONS["porta-potty-rental-oakland-ca/index.html"] = r"""<section id="services" class="py-20 bg-gray-50">
  <div class="container mx-auto px-4">
    <div class="text-center mb-16">
      <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Complete Portable Sanitation Services in Oakland, CA</h2>
      <p class="text-gray-600 mb-6 leading-relaxed max-w-3xl mx-auto">
        From heavy-duty units built for the Port of Oakland to elegant VIP trailers for weddings in the hills, we carry the exact portable toilet rental Oakland needs. 
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden transition-transform duration-300 hover:shadow-lg">
        <img loading="lazy" src="../service-images/construction-porta-potty-rentals/26. 20260224_191415_839.webp" width="352" height="192" alt="Construction Porta Potty Rentals Oakland CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2">Construction Porta Potty Rentals</h3>
          <p class="text-gray-600 text-sm mb-3">Keep your Oakland job site compliant and workers productive. We offer rugged units with reliable weekly pump-outs for all Alameda County builds.</p>
        </div>
        <div class="flex justify-center items-center mb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden transition-transform duration-300 hover:shadow-lg">
        <img loading="lazy" src="../service-images/standard-porta-potty/portable-temporary-toilet-is-located-on-construction-site.webp" width="352" height="192" alt="Standard Porta Potty Oakland CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2">Standard Porta Potty</h3>
          <p class="text-gray-600 text-sm mb-3">The cost-effective backbone of portable sanitation in Oakland. Well-ventilated, impeccably clean, and perfect for short-term events or home renovations.</p>
        </div>
        <div class="flex justify-center items-center mb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden transition-transform duration-300 hover:shadow-lg">
        <img loading="lazy" src="../service-images/ada-compliant-units/17. 20260226_142708_823.webp" width="352" height="192" alt="ADA-Compliant Units Oakland CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2">ADA-Compliant Units</h3>
          <p class="text-gray-600 text-sm mb-3">Ensure complete accessibility at your Oakland event. These oversized, wheelchair-accessible restrooms meet strict California ADA requirements.</p>
        </div>
        <div class="flex justify-center items-center mb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden transition-transform duration-300 hover:shadow-lg">
        <img loading="lazy" src="../service-images/luxary-restroom-trailers/14. 20260226_141800_171.webp" width="352" height="192" alt="Luxury Restroom Trailers Oakland CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2">Luxury Restroom Trailers</h3>
          <p class="text-gray-600 text-sm mb-3">Elevate VIP events near Lake Merritt with climate-controlled, multi-stall trailers featuring flushing toilets, running water, and elegant interiors.</p>
        </div>
        <div class="flex justify-center items-center mb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden transition-transform duration-300 hover:shadow-lg">
        <img loading="lazy" src="../service-images/portable-sinks-rental-optimized/2. 20260226_154636_342.webp" width="352" height="192" alt="Portable Sinks / Hand Wash Stations Oakland CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2">Hand Wash Stations</h3>
          <p class="text-gray-600 text-sm mb-3">Standalone foot-pump sinks fully stocked with soap and towels. Vital for Oakland food festivals and maintaining OSHA compliance on job sites.</p>
        </div>
        <div class="flex justify-center items-center mb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden transition-transform duration-300 hover:shadow-lg">
        <img loading="lazy" src="../service-images/flushable-portable-toilets/22. 20260226_190018_643.webp" width="352" height="192" alt="Flushable Portable Toilets Oakland CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2">Flushable Portable Toilets</h3>
          <p class="text-gray-600 text-sm mb-3">A premium upgrade to the standard unit, these porta potties feature a closed-bowl foot-flush system, minimizing odors for upscale Oakland gatherings.</p>
        </div>
        <div class="flex justify-center items-center mb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden transition-transform duration-300 hover:shadow-lg">
        <img loading="lazy" src="../service-images/construction-porta-potty-rentals/3. 20260226_135913_274.webp" width="352" height="192" alt="Crane Hook Porta Potty Rentals Oakland CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2">Crane Hook Porta Potty Rentals</h3>
          <p class="text-gray-600 text-sm mb-3">Essential for Downtown Oakland high-rise construction. Securely lift these specialized units to upper floors so crews stay working efficiently.</p>
        </div>
        <div class="flex justify-center items-center mb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden transition-transform duration-300 hover:shadow-lg">
        <img loading="lazy" src="../service-images/porta-potty-on Trailer – Trailer Mounted Porta Potty Rentals/1. 20260226_222458_928.webp" width="352" height="192" alt="Trailer Mounted Porta Potty Rentals Oakland CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2">Trailer Mounted Units</h3>
          <p class="text-gray-600 text-sm mb-3">Perfect for agricultural sites, highway roadwork, or moving between locations in the Oakland Hills. Towable, rugged, and highly convenient.</p>
        </div>
        <div class="flex justify-center items-center mb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden transition-transform duration-300 hover:shadow-lg">
        <img loading="lazy" src="../service-images/septic-pumping-and-holding-tanks-optimized/17. 20260226_143925_319.webp" width="352" height="192" alt="Septic Pumping & Holding Tanks Oakland CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2">Septic Pumping & Holding Tanks</h3>
          <p class="text-gray-600 text-sm mb-3">We provide large-capacity holding tanks for RVs, job trailers, and long-term sites in Oakland, complete with scheduled pump-out services.</p>
        </div>
        <div class="flex justify-center items-center mb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden transition-transform duration-300 hover:shadow-lg">
        <img loading="lazy" src="../service-images/event-restroom-trailers/6. 20260226_154342_260.webp" width="352" height="192" alt="Event Restroom Trailers Oakland CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2">Event Restroom Trailers</h3>
          <p class="text-gray-600 text-sm mb-3">Designed to handle massive crowds at Jack London Square or the Oakland Coliseum. Multiple stalls minimize lines while maintaining high sanitation standards.</p>
        </div>
        <div class="flex justify-center items-center mb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden transition-transform duration-300 hover:shadow-lg">
        <img loading="lazy" src="../service-images/emergency -Short-Term Rentals/18. 20260301_225640_618.webp" width="352" height="192" alt="Emergency / Short-Term Rentals Oakland CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2">Emergency / Short-Term Rentals</h3>
          <p class="text-gray-600 text-sm mb-3">Water main break? Plumbing failure? Our Oakland dispatch team operates 24/7 to deliver emergency sanitation relief exactly when you need it.</p>
        </div>
        <div class="flex justify-center items-center mb-5 mt-auto">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden transition-transform duration-300 hover:shadow-lg">
        <img loading="lazy" src="../service-images/deluxe-porta-potty/2. 20260226_145947_995.webp" width="352" height="192" alt="Deluxe Porta Potty Oakland CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold mb-2">Deluxe Porta Potty</h3>
          <p class="text-gray-600 text-sm mb-3">A highly requested unit for Oakland private parties. It includes a built-in handwashing sink, mirror, and extra interior space for guest comfort.</p>
        </div>
        <div class="flex justify-center items-center mb-5 mt-auto">
          Get a Quote
        </div>
      </div>
    </div>
  </div>
</section>"""

# ---------- Paradise ----------
ORIGINAL_SECTIONS["porta-potty-rental-paradise-ca/index.html"] = r"""<section id="services" class="py-20 bg-white">
  <div class="container mx-auto px-4">
    <div class="text-center mb-16">
      <h2 class="text-3xl md:text-4xl font-extrabold text-gray-900 mb-4">Complete Porta Potty Rentals in Paradise, CA</h2>
        <p class="text-gray-600 text-lg max-w-3xl mx-auto">
          From basic construction units in <strong>Magalia</strong> to luxury trailers for downtown Paradise events, explore our comprehensive fleet.
        </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="flex flex-col bg-gray-50 rounded-xl border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/construction-porta-potty-rentals/4. 20260226_140341_252.webp" width="352" height="192" alt="Construction Porta Potty Rentals Paradise CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Construction Porta Potty Rentals</h3>
          <p class="text-gray-600 text-sm mb-3">Rugged and reliable portable toilets engineered for Paradise rebuilding sites. Includes weekly pump-outs.</p>
        </div>
        <div class="px-5 pb-5">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-gray-50 rounded-xl border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/luxary-restroom-trailers/7. 20260226_141103_109.webp" width="352" height="192" alt="Luxury Restroom Trailers Paradise CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Luxury Restroom Trailers</h3>
          <p class="text-gray-600 text-sm mb-3">Elevate your Butte County wedding with premium trailers featuring climate control, sinks, and flushing toilets.</p>
        </div>
        <div class="px-5 pb-5">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-gray-50 rounded-xl border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/ada-compliant-units/12. 20260226_143219_667.webp" width="352" height="192" alt="ADA Compliant Units Paradise" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">ADA-Compliant Units</h3>
          <p class="text-gray-600 text-sm mb-3">Oversized, wheelchair-accessible portable restrooms designed for public events and code-compliant job sites in Paradise.</p>
        </div>
        <div class="px-5 pb-5">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-gray-50 rounded-xl border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/standard-porta-potty/porta-potty-green-and-grey-at-golf-course-under-tree.webp" width="352" height="192" alt="Standard Porta Potty Paradise" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Standard Porta Potty</h3>
          <p class="text-gray-600 text-sm mb-3">Our classic, cost-effective sanitation solution. Delivered spotless and ready for immediate use in zip code 95969.</p>
        </div>
        <div class="px-5 pb-5">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-gray-50 rounded-xl border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/handwash-stations/10. 20260226_151831_968.webp" width="352" height="192" alt="Hand Wash Stations Paradise" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Hand Wash Stations</h3>
          <p class="text-gray-600 text-sm mb-3">Freestanding sinks with fresh water, soap, and towels to keep Paradise workers and event guests hygienic.</p>
        </div>
        <div class="px-5 pb-5">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-gray-50 rounded-xl border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/flushable-portable-toilets/6. 20260226_185824_761.webp" width="352" height="192" alt="Flushable Portable Toilets Paradise CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Flushable Portable Toilets</h3>
          <p class="text-gray-600 text-sm mb-3">Upgraded porta potties equipped with a foot-pump flush mechanism to hide waste, ideal for private parties in Magalia.</p>
        </div>
        <div class="px-5 pb-5">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-gray-50 rounded-xl border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/septic-pumping-and-holding-tanks-optimized/4. 20260226_144141_718.webp" width="352" height="192" alt="Septic Pumping Paradise CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Septic Pumping & Holding Tanks</h3>
          <p class="text-gray-600 text-sm mb-3">Reliable pumping service and large holding tank rentals for sites lacking direct sewer hookups across the ridge.</p>
        </div>
        <div class="px-5 pb-5">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-gray-50 rounded-xl border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/event-restroom-trailers/3. 20260226_152839_543.webp" width="352" height="192" alt="Event Restroom Trailers Paradise" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Event Restroom Trailers</h3>
          <p class="text-gray-600 text-sm mb-3">High-capacity restroom trailers perfect for community festivals and gatherings in Downtown Paradise.</p>
        </div>
        <div class="px-5 pb-5">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-gray-50 rounded-xl border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/emergency -Short-Term Rentals/7. 20260301_223123_238.webp" width="352" height="192" alt="Emergency Rentals Paradise CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Emergency / Short-Term Rentals</h3>
          <p class="text-gray-600 text-sm mb-3">Rapid deployment of portable toilets for emergency water shutoffs or disaster response in Butte County.</p>
        </div>
        <div class="px-5 pb-5">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-gray-50 rounded-xl border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/deluxe-porta-potty/6. 20260226_151023_590.webp" width="352" height="192" alt="Deluxe Porta Potty Paradise" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Deluxe Porta Potty</h3>
          <p class="text-gray-600 text-sm mb-3">Slightly larger footprint with an interior mirror and shelf. A great middle-ground for Paradise home renovations.</p>
        </div>
        <div class="px-5 pb-5">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-gray-50 rounded-xl border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/rolling-porta-potty-for-rent-optimized/5. 20260226_192451_637.webp" width="352" height="192" alt="Crane Hook Porta Potty Paradise CA" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Crane Hook Porta Potty</h3>
          <p class="text-gray-600 text-sm mb-3">Designed with reinforced lifting points, allowing units to be hoisted safely onto elevated Paradise construction levels.</p>
        </div>
        <div class="px-5 pb-5">
          Get a Quote
        </div>
      </div>

      <div class="flex flex-col bg-gray-50 rounded-xl border border-gray-100 overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <img loading="lazy" src="../service-images/porta-potty-on Trailer – Trailer Mounted Porta Potty Rentals/24. 20260226_223237_737.webp" width="352" height="192" alt="Trailer Mounted Porta Potty Paradise" class="w-full h-48 object-cover">
        <div class="p-5 flex-grow">
          <h3 class="text-lg font-bold text-gray-900 mb-2">Porta Potty on Trailer</h3>
          <p class="text-gray-600 text-sm mb-3">Mobile units mounted on single-axle trailers. Perfect for moving crews doing roadwork along the Skyway corridor.</p>
        </div>
        <div class="px-5 pb-5">
          Get a Quote
        </div>
      </div>
    </div>
  </div>
</section>"""


# ============================================================
# RESTORE files: replace corrupted services section with original
# ============================================================

print("=" * 60)
print("RESTORING CORRUPTED FILES")
print("=" * 60)

for rel_path, orig_section in ORIGINAL_SECTIONS.items():
    fpath = os.path.join(BASE, rel_path)
    
    with open(fpath, "r", encoding="utf-8") as f:
        full = f.read()
    
    # Find the services section boundaries
    sec_start = full.find('<section id="services"')
    if sec_start == -1:
        print(f"❌ No services section in {rel_path}")
        continue
    
    # Find the closing </section> that matches
    # Count open/close to handle nested divs
    search_pos = sec_start
    depth = 0
    found_end = False
    while search_pos < len(full):
        open_tag = full.find("<section", search_pos)
        close_tag = full.find("</section>", search_pos)
        
        if close_tag == -1:
            break
        
        # Check if there's an open tag before the close tag
        if open_tag != -1 and open_tag < close_tag and open_tag != sec_start:
            depth += 1
            search_pos = open_tag + 8
        else:
            if depth == 0:
                sec_end = close_tag + len("</section>")
                found_end = True
                break
            else:
                depth -= 1
                search_pos = close_tag + len("</section>")
    
    if not found_end:
        print(f"❌ Could not find section end in {rel_path}")
        continue
    
    before = full[:sec_start]
    after = full[sec_end:]
    
    # Reconstruct
    restored = before + orig_section + after
    
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(restored)
    
    # Validate
    new_sec_start = restored.find('<section id="services"')
    new_sec = restored[new_sec_start:new_sec_start + len(orig_section)]
    if new_sec == orig_section:
        print(f"✅ Restored {rel_path}")
    else:
        print(f"⚠️  Possible mismatch in {rel_path} - checking...")
        if new_sec[:50] == orig_section[:50] and new_sec[-50:] == orig_section[-50:]:
            print(f"   Ends match - OK")
        else:
            print(f"   MISMATCH!")
            print(f"   New: {new_sec[:80]!r}")
            print(f"   Orig: {orig_section[:80]!r}")

print()
print("=" * 60)
print("CORRECTED REPLACEMENT SCRIPT")
print("=" * 60)

# ============================================================
# SERVICE URL MAPPING
# ============================================================
BASE_URL = "https://fixpilotportapottyrentals.com/services"

SERVICE_KEYWORDS = [
    ("crane-hook", f"{BASE_URL}/crane-hook-porta-potty-rentals"),
    ("crane hook", f"{BASE_URL}/crane-hook-porta-potty-rentals"),
    ("luxury", f"{BASE_URL}/luxury-restroom-trailers"),
    ("flushable", f"{BASE_URL}/flushable-portable-toilets"),
    ("construction", f"{BASE_URL}/construction-porta-potty-rentals"),
    ("standard", f"{BASE_URL}/standard-porta-potty"),
    ("deluxe", f"{BASE_URL}/deluxe-porta-potty"),
    ("ada", f"{BASE_URL}/ada-compliant-units"),
    ("hand wash", f"{BASE_URL}/hand-wash-stations"),
    ("hand sanitizer", f"{BASE_URL}/hand-wash-stations"),
    ("event restroom", f"{BASE_URL}/event-restroom-trailers"),
    ("septic", f"{BASE_URL}/septic-pumping-holding-tanks"),
    ("holding tank", f"{BASE_URL}/septic-pumping-holding-tanks"),
    ("porta potty on trailer", f"{BASE_URL}/porta-potty-on-trailer"),
    ("trailer mounted", f"{BASE_URL}/porta-potty-on-trailer"),
    ("on trailer", f"{BASE_URL}/porta-potty-on-trailer"),
    ("vip", f"{BASE_URL}/vip-trailers-rental"),
    ("emergency", f"{BASE_URL}/emergency-short-term-rentals"),
    ("disaster", f"{BASE_URL}/emergency-short-term-rentals"),
    ("short-term", f"{BASE_URL}/emergency-short-term-rentals"),
    ("rolling", f"{BASE_URL}/rolling-porta-potty-rental"),
    ("restroom", f"{BASE_URL}/luxury-restroom-trailers"),
    ("trailer", f"{BASE_URL}/luxury-restroom-trailers"),
    ("fancy", f"{BASE_URL}/fancy-portable-restroom-trailers-for-rent"),
]


def get_url(h3_text):
    t = h3_text.lower().strip()
    for keyword, url in SERVICE_KEYWORDS:
        if keyword in t:
            return url
    print(f"  ⚠ NO MATCH: {h3_text!r}")
    return None


# ============================================================
# FILE-SPECIFIC CONFIG: div classes and anchor anchor classes
# ============================================================
FILE_CONFIGS = {
    "porta-potty-rental-arlington-tx/index.html": {
        "div_classes": 'px-8 pb-8 mt-auto',
        "anchor_classes": 'px-8 pb-8 mt-auto font-bold text-gray-700 hover:text-cta transition block',
        "is_phone_link": False,
    },
    "porta-potty-rental-frederick-md/index.html": {
        "div_classes": 'px-5 pb-5 mt-auto',
        "anchor_classes": 'px-5 pb-5 mt-auto font-bold text-gray-700 hover:text-cta transition block',
        "is_phone_link": False,
    },
    "porta-potty-rental-glendale-ca/index.html": {
        "div_classes": 'px-8 pb-8 mt-auto',
        "anchor_classes": 'px-8 pb-8 mt-auto font-bold text-gray-700 hover:text-brand-800 transition block',
        "is_phone_link": False,
    },
    "porta-potty-rental-mesa-az/index.html": {
        "div_classes": 'px-8 pb-8 mt-auto',
        "anchor_classes": 'px-8 pb-8 mt-auto font-bold text-gray-700 hover:text-cta transition block',
        "is_phone_link": False,
    },
    "porta-potty-rental-naperville-il/index.html": {
        "div_classes": None,  # Naperville has phone links, not plain divs
        "anchor_classes": 'phone-link bg-cta text-white w-full py-3 rounded-xl font-bold inline-block hover:bg-orange-700 transition',
        "is_phone_link": True,
    },
    "porta-potty-rental-oakland-ca/index.html": {
        "div_classes": 'flex justify-center items-center mb-5 mt-auto',
        "anchor_classes": 'flex justify-center items-center mb-5 mt-auto text-gray-700 hover:text-green-600 font-medium',
        "is_phone_link": False,
    },
    "porta-potty-rental-paradise-ca/index.html": {
        "div_classes": 'px-5 pb-5',
        "anchor_classes": 'px-5 pb-5 font-bold text-gray-700 hover:text-cta transition block',
        "is_phone_link": False,
    },
}


def process_file(rel_path):
    fpath = os.path.join(BASE, rel_path)
    config = FILE_CONFIGS[rel_path]
    
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Find services section
    sec_start = html.find('<section id="services"')
    if sec_start == -1:
        print(f"  ❌ No services section")
        return False
    
    # Find matching </section>
    depth = 0
    pos = sec_start
    while pos < len(html):
        os_tag = html.find("<section", pos)
        cs_tag = html.find("</section>", pos)
        if cs_tag == -1:
            print(f"  ❌ No closing section")
            return False
        if os_tag != -1 and os_tag < cs_tag and os_tag != sec_start:
            depth += 1
            pos = os_tag + 8
        else:
            if depth == 0:
                sec_end = cs_tag + len("</section>")
                break
            depth -= 1
            pos = cs_tag + len("</section>")
    
    section = html[sec_start:sec_end]
    
    # Find all h3 elements in section with positions
    h3_positions = []
    h3_pattern = re.compile(r'<h3[^>]*>(.*?)</h3>')
    for m in h3_pattern.finditer(section):
        h3_positions.append((m.start(), m.end(), m.group(1).strip()))
    
    if not h3_positions:
        print(f"  ❌ No service cards found")
        return False
    
    print(f"  Found {len(h3_positions)} cards")
    
    # Build list of (start_pos, end_pos, replacement_text) - in REVERSE order
    replacements = []
    
    for i, (h3_start, h3_end, h3_text) in enumerate(h3_positions):
        url = get_url(h3_text)
        if url is None:
            continue
        
        # Determine search range: after this h3, before next h3 (or end of section)
        search_start = h3_end
        if i + 1 < len(h3_positions):
            search_end = h3_positions[i + 1][0]
        else:
            search_end = len(section)
        
        card_area = section[search_start:search_end]
        
        if config["is_phone_link"]:
            # Naperville: find existing <a> with tel: href
            a_re = re.compile(r'<a\s[^>]*href="tel:\+?1?\d*"[^>]*>\s*Get a Quote\s*</a>', re.DOTALL)
            a_match = a_re.search(card_area)
            if a_match:
                old_tag = a_match.group(0)
                new_tag = old_tag.replace('href="tel:+18336529344"', f'href="{url}"')
                replacements.append((
                    search_start + a_match.start(),
                    search_start + a_match.end(),
                    new_tag
                ))
                print(f"    Phone link: {h3_text} -> {url}")
            else:
                print(f"    ⚠ No phone link found for: {h3_text}")
        else:
            # Find plain div with "Get a Quote"
            div_re = re.compile(
                rf'<div\s+class="{re.escape(config["div_classes"])}"\s*>\s*\n\s*Get a Quote\s*\n\s*</div>',
                re.DOTALL
            )
            div_match = div_re.search(card_area)
            if div_match:
                old_div = div_match.group(0)
                new_anchor = f'<a href="{url}" class="{config["anchor_classes"]}">\n          Get a Quote\n        </a>'
                replacements.append((
                    search_start + div_match.start(),
                    search_start + div_match.end(),
                    new_anchor
                ))
                print(f"    Replaced: {h3_text} -> {url}")
            else:
                # Try without newline matching
                div_re2 = re.compile(
                    rf'<div\s+class="{re.escape(config["div_classes"])}"[^>]*>\s*Get a Quote\s*</div>',
                    re.DOTALL
                )
                div_match2 = div_re2.search(card_area)
                if div_match2:
                    old_div = div_match2.group(0)
                    new_anchor = f'<a href="{url}" class="{config["anchor_classes"]}">Get a Quote</a>'
                    replacements.append((
                        search_start + div_match2.start(),
                        search_start + div_match2.end(),
                        new_anchor
                    ))
                    print(f"    Replaced(no-nl): {h3_text} -> {url}")
                else:
                    print(f"    ⚠ No div found for: {h3_text}")
    
    # Process replacements in REVERSE order (last card first)
    replacements.sort(key=lambda x: x[0], reverse=True)
    
    modified_section = section
    for start, end, new_text in replacements:
        modified_section = modified_section[:start] + new_text + modified_section[end:]
    
    # Reconstruct full HTML
    html = html[:sec_start] + modified_section + html[sec_end:]
    
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"  ✅ {len(replacements)} replacements in {rel_path}")
    return True


for rel_path in FILE_CONFIGS:
    print(f"\n--- {rel_path} ---")
    process_file(rel_path)

print("\n✅ Done! All files processed.")
