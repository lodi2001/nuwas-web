import { SectionHeader, Product } from "@/lib/types";
import SectionTitle from "./SectionTitle";

export default function ProductsSection({
  header,
  products,
}: {
  header: SectionHeader;
  products: Product[];
}) {
  return (
    <section className="section-padding products-section" id="products">
      <div className="pattern-decoration products-pattern-left" />
      <div className="pattern-decoration products-pattern-right" />
      <div className="container" style={{ position: "relative", zIndex: 2 }}>
        <SectionTitle header={header} />
        <div className="card-grid">
          {products.map((product) => (
            <div
              className="card product-card"
              key={product.name}
            >
              <div className="pattern-decoration product-card-pattern" />
              <h4 style={{ color: "var(--accent-cyan)", marginBottom: "10px" }}>
                {product.name}
              </h4>
              <p>{product.description_ar}</p>
              <ul style={{ margin: "15px 20px", fontSize: "0.9rem" }}>
                {product.features_list_ar.map((feature) => (
                  <li key={feature}>{feature}</li>
                ))}
              </ul>
              {product.link && (
                <a
                  href={product.link}
                  className="btn btn-outline"
                  style={{ padding: "5px 20px" }}
                >
                  المزيد
                </a>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
