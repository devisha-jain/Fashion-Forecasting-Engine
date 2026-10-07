"use client";

/* eslint-disable @next/next/no-img-element */

interface LightboxProps {
  isOpen: boolean;
  title: string;
  images: string[];
  currentIndex: number;
  setCurrentIndex: (index: number) => void;
  onClose: () => void;
}

export default function Lightbox({
  isOpen,
  title,
  images,
  currentIndex,
  setCurrentIndex,
  onClose,
}: LightboxProps) {
  if (!isOpen) return null;

  const prevImage = () => {
    setCurrentIndex(
      (currentIndex - 1 + images.length) % images.length
    );
  };

  const nextImage = () => {
    setCurrentIndex((currentIndex + 1) % images.length);
  };

  return (
    <div className={`lightbox ${isOpen ? "active" : ""}`}>
      <div className="lightbox-close" onClick={onClose}>
        &times;
      </div>
      <div className="lightbox-content">
        <img
          src={images[currentIndex]}
          className="lightbox-img"
          alt={title}
        />
        <div className="lightbox-prev" onClick={prevImage}>
          &#10094;
        </div>
        <div className="lightbox-next" onClick={nextImage}>
          &#10095;
        </div>
      </div>
      <div className="lightbox-title">{title}</div>
    </div>
  );
}
