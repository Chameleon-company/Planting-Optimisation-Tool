import "./heroTreeline.css";

// [x, file, width, height, animDelay (s), animDuration (s)]
type TreeSpec = [number, string, number, number, number, number];

const TREES: TreeSpec[] = [
  [60, "tree1.svg", 180, 220, 0.0, 7.0],
  [160, "tree2.svg", 90, 160, 1.4, 5.5],
  [270, "tree3.svg", 200, 130, 0.7, 8.2],
  [410, "tree4.svg", 180, 240, 2.1, 6.3],
  [530, "tree1.svg", 160, 120, 0.3, 9.1],
  [630, "tree3.svg", 170, 190, 1.8, 5.8],
  [760, "tree2.svg", 130, 170, 0.9, 7.6],
  [855, "tree4.svg", 80, 200, 1.5, 6.8],
  [950, "tree1.svg", 250, 250, 0.1, 8.5],
  [1065, "tree2.svg", 130, 130, 2.3, 5.2],
  [1170, "tree3.svg", 120, 120, 0.0, 7.0],
  [1270, "tree2.svg", 95, 110, 1.4, 5.5],
  [1360, "tree1.svg", 160, 160, 0.7, 8.2],
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
      {TREES.map(([x, file, w, h, delay, duration], i) => (
        <g key={i} transform={`translate(${x}, 300)`}>
          <g
            className="hero-tree"
            style={{
              animationDelay: `${delay}s`,
              animationDuration: `${duration}s`,
            }}
          >
            <image
              href={`/assets/images/trees/${file}`}
              preserveAspectRatio="xMidYMax meet"
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
