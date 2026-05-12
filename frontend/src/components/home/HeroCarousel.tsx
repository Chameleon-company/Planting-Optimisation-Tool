import { useState, useEffect } from "react";

interface HeroCarouselProps {
  images: string[];
  interval?: number;
}

export default function HeroCarousel({
  images,
  interval = 4000,
}: HeroCarouselProps) {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    if (images.length <= 1) return;
    const timer = setInterval(() => {
      setCurrent(i => (i + 1) % images.length);
    }, interval);
    return () => clearInterval(timer);
  }, [images.length, interval]);

  return (
    <div className="heroCarousel">
      {images.map((src, i) => (
        <img
          key={src}
          src={src}
          alt=""
          className={`heroCarouselImg ${i === current ? "heroCarouselImg--active" : ""}`}
        />
      ))}
      <div className="heroCarouselDots">
        {images.map((src, i) => (
          <button
            key={src}
            className={`heroCarouselDot ${i === current ? "heroCarouselDot--active" : ""}`}
            onClick={() => setCurrent(i)}
            aria-label={`Go to image ${i + 1}`}
          />
        ))}
      </div>
    </div>
  );
}
