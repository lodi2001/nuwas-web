"use client";

import { useEffect, useRef } from "react";
import Image from "next/image";
import { SectionHeader, Product } from "@/lib/types";

// Fallback logo map for static assets
const FALLBACK_LOGOS: Record<string, string> = {
  "NUVIDEO.AI": "/products/nuvideo.ai-v2.jpeg",
  "NuSport.AI": "/products/Nusportai.png",
  "NuChat": "/products/Nuchat.png",
  "NuFIX": "/products/Nufix.png",
  "Magic Report": "/products/Numagic.png",
  "NuPedia Research": "/products/Nupedia.png",
  "DrivUp": "/products/driveup.png",
  "NSB": "/products/NSB.svg",
};

interface NodeConfig {
  seedX: number;
  seedY: number;
  speed: number;
  radius: number;
}

export default function NeuralProductsSection({
  header,
  products,
}: {
  header: SectionHeader;
  products: Product[];
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const coreRef = useRef<HTMLDivElement>(null);
  const nodeRefs = useRef<(HTMLDivElement | null)[]>([]);
  const configsRef = useRef<NodeConfig[]>([]);

  // Initialize node configs once
  useEffect(() => {
    configsRef.current = products.map((_, i) => ({
      seedX: (i * 73.7 + 17) % 100,
      seedY: (i * 41.3 + 53) % 100,
      speed: 0.0006 + (i * 0.00008),
      radius: 15 + (i % 3) * 7,
    }));
  }, [products]);

  // Animation loop — direct DOM manipulation, no re-renders
  useEffect(() => {
    let animId: number;

    function animate(time: number) {
      const container = containerRef.current;
      const svg = svgRef.current;
      const core = coreRef.current;
      if (!container || !svg || !core) {
        animId = requestAnimationFrame(animate);
        return;
      }

      const containerRect = container.getBoundingClientRect();
      const coreRect = core.getBoundingClientRect();
      const coreX = coreRect.left - containerRect.left + coreRect.width / 2;
      const coreY = coreRect.top - containerRect.top + coreRect.height / 2;

      let svgHTML = `
        <defs>
          <linearGradient id="ng" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#003399" />
            <stop offset="50%" stop-color="#40c4ff" />
            <stop offset="100%" stop-color="#003399" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>
      `;

      nodeRefs.current.forEach((nodeEl, i) => {
        if (!nodeEl) return;
        const cfg = configsRef.current[i];
        if (!cfg) return;

        // Organic drift
        const offsetX = Math.sin(time * cfg.speed + cfg.seedX) * cfg.radius;
        const offsetY = Math.cos(time * cfg.speed * 0.8 + cfg.seedY) * cfg.radius;
        nodeEl.style.transform = `translate(${offsetX}px, ${offsetY}px)`;

        // Get node center
        const rect = nodeEl.getBoundingClientRect();
        const nodeX = rect.left - containerRect.left + rect.width / 2;
        const nodeY = rect.top - containerRect.top + rect.height / 2;

        // Bezier control point — offset for curve effect
        const midX = (coreX + nodeX) / 2;
        const midY = (coreY + nodeY) / 2;
        const ctrlX = midX + (coreY - nodeY) * 0.15;
        const ctrlY = midY + (nodeX - coreX) * 0.15;

        svgHTML += `<path class="neural-path" d="M ${coreX} ${coreY} Q ${ctrlX} ${ctrlY} ${nodeX} ${nodeY}"></path>`;
        svgHTML += `<circle class="neural-joint" cx="${nodeX}" cy="${nodeY}" r="5" filter="url(#glow)"></circle>`;
      });

      // Core synapse
      svgHTML += `<circle class="neural-joint core-joint" cx="${coreX}" cy="${coreY}" r="7" filter="url(#glow)"></circle>`;

      svg.innerHTML = svgHTML;
      animId = requestAnimationFrame(animate);
    }

    animId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animId);
  }, [products]);

  // Calculate base positions in a circle
  const getNodeStyle = (index: number, total: number): React.CSSProperties => {
    const angle = (index / total) * 2 * Math.PI - Math.PI / 2;
    const radiusX = 38; // % from center
    const radiusY = 36;
    const left = 50 + radiusX * Math.cos(angle);
    const top = 50 + radiusY * Math.sin(angle);
    return {
      position: "absolute",
      left: `${left}%`,
      top: `${top}%`,
    };
  };

  return (
    <section className="neural-section" id="products">
      <div className="container section-title" data-aos="fade-down">
        <h2>{header.title_ar}</h2>
        <p>{header.subtitle_ar}</p>
      </div>

      <div className="network-container" ref={containerRef}>
        <svg className="neural-svg" ref={svgRef} />

        {/* Central Nuwas Core */}
        <div className="core-node" ref={coreRef}>
          <Image
            src="/logo.png"
            alt="Nuwas Core"
            width={160}
            height={60}
            style={{ width: "100%", height: "auto", objectFit: "contain" }}
          />
        </div>

        {/* Product Nodes */}
        {products.map((product, i) => {
          let logoSrc = product.logo || FALLBACK_LOGOS[product.name] || "/logo.png";
          // Rewrite API logo URLs to use /media/ proxy path
          if (logoSrc && logoSrc.includes("/media/")) {
            const mediaPath = logoSrc.match(/\/media\/.+/)?.[0];
            if (mediaPath) logoSrc = mediaPath;
          }
          return (
            <div
              key={product.name}
              className="product-node"
              style={getNodeStyle(i, products.length)}
              ref={(el) => { nodeRefs.current[i] = el; }}
            >
              <Image
                src={logoSrc}
                alt={product.name}
                width={120}
                height={60}
                style={{ maxWidth: "90%", maxHeight: "60px", objectFit: "contain" }}
                unoptimized
              />
              <span>{product.name}</span>
              <div className="product-tooltip">
                <strong>{product.name}</strong>
                <p>{product.description_ar}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
