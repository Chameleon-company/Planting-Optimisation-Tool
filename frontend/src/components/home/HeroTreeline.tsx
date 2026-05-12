import "./heroTreeline.css";

// [x, file, width, height, animDelay (s)]
type TreeSpec = [number, string, number, number, number];

const TREES: TreeSpec[] = [
  [60, "tree1.svg", 130, 185, 0.0],
  [175, "tree2.svg", 120, 165, 1.4],
  [290, "tree3.svg", 150, 210, 0.7],
  [415, "tree4.svg", 135, 190, 2.1],
  [530, "tree1.svg", 160, 225, 0.3],
  [650, "tree2.svg", 115, 160, 1.8],
  [760, "tree3.svg", 145, 200, 0.9],
  [875, "tree4.svg", 130, 180, 1.5],
  [985, "tree1.svg", 155, 215, 0.1],
  [1095, "tree2.svg", 125, 170, 2.3],
];

export default function HeroTreeline() {
  return (
    <svg
      className="hero-treeline"
      viewBox="0 0 1440 300"
      preserveAspectRatio="xMidYMax slice"
      style={{ overflow: "visible" }}
      aria-hidden="true"
    >
      {TREES.map(([x, file, w, h, delay], i) => (
        <g key={i} transform={`translate(${x}, 300)`}>
          <g className="hero-tree" style={{ animationDelay: `${delay}s` }}>
            <image
              href={`/assets/images/trees/${file}`}
              x={-w / 2}
              y={-h}
              width={w}
              height={h}
            />
          </g>
        </g>
      ))}
    </svg>
  );
}
