"use client";

/* eslint-disable @next/next/no-img-element */

interface MoodboardSectionProps {
  openLightbox: (title: string, images: string[]) => void;
}

interface Moodboard {
  /** Heading shown under the collage */
  label: string;
  /** Title shown in the lightbox when the collage is opened */
  title: string;
  /** Alt-text prefix; images are labelled "<alt> 1..n" */
  alt: string;
  /** Images in the order they appear in the collage */
  collage: string[];
  /** Images in the order they appear in the lightbox */
  lightbox: string[];
}

const img = (name: string) => `/images/${name}`;

const MOODBOARDS: Moodboard[] = [
  {
    label: "A very pastel spring",
    title: "A very Pastel Spring",
    alt: "Pastel Spring",
    collage: ["butter_yellow.jpg", "spring_mood_2.jpg", "spring_mood_3.jpg"].map(img),
    lightbox: ["butter_yellow.jpg", "spring_mood_2.jpg", "spring_mood_3.jpg"].map(img),
  },
  {
    label: "Iced matcha coquette summer",
    title: "Iced matcha coquette summer",
    alt: "Matcha Summer",
    collage: ["spring_mood_1.jpg", "summer_mood_2.jpg", "summer_mood_3.jpg"].map(img),
    lightbox: ["spring_mood_1.jpg", "summer_mood_2.jpg", "summer_mood_3.jpg"].map(img),
  },
  {
    label: "Espresso girl fall",
    title: "Espresso girl Fall",
    alt: "Espresso Fall",
    collage: ["brown_fall_girls.jpg", "espresso_fall_1.jpg", "espresso_fall_2.jpg"].map(img),
    lightbox: ["espresso_fall_1.jpg", "espresso_fall_2.jpg", "brown_fall_girls.jpg"].map(img),
  },
  {
    label: "Winter in vintage tones",
    title: "Winter in Vintage Tones",
    alt: "Vintage Winter",
    collage: ["vintage_winter.jpg", "vintage_winter_2.jpg", "vintage_winter_3.jpg"].map(img),
    lightbox: ["vintage_winter.jpg", "vintage_winter_2.jpg", "vintage_winter_3.jpg"].map(img),
  },
  {
    label: "Wedding season winter",
    title: "Wedding Season Winter",
    alt: "Wedding",
    collage: ["wedding_2.jpg", "wedding_1.jpg", "wedding_3.jpg"].map(img),
    lightbox: ["wedding_1.jpg", "wedding_2.jpg", "wedding_3.jpg"].map(img),
  },
  {
    label: "Festive season outfits",
    title: "Festive season outfits",
    alt: "Festive",
    collage: ["festive_1.jpg", "festive_2.jpg", "festive_orange.jpg"].map(img),
    lightbox: ["festive_1.jpg", "festive_2.jpg", "festive_orange.jpg"].map(img),
  },
  {
    label: "Ethnic streetwear summer",
    title: "Ethnic streetwear summer",
    alt: "Ethnic Summer",
    collage: ["ethnic_summer_1.png", "ethnic_summer_2.png", "ethnic_summer_3.png"].map(img),
    lightbox: ["ethnic_summer_1.png", "ethnic_summer_2.png", "ethnic_summer_3.png"].map(img),
  },
  {
    label: "Chai-toned october",
    title: "Chai-toned october",
    alt: "Chai October",
    collage: ["chai_october_1.png", "chai_october_2.png", "chai_october_3.png"].map(img),
    lightbox: ["chai_october_1.png", "chai_october_2.png", "chai_october_3.png"].map(img),
  },
  {
    label: "Sunsets on a digicam",
    title: "Sunsets on a digicam",
    alt: "Sunset",
    collage: ["sunset_3.jpg", "sunset_2.jpg", "sunset_1.jpg"].map(img),
    lightbox: ["sunset_3.jpg", "sunset_1.jpg", "sunset_2.jpg"].map(img),
  },
];

export default function MoodboardSection({
  openLightbox,
}: MoodboardSectionProps) {
  return (
    <div className="box moodboard-box">
      <h2>Social Trend Report: Instagram Edition</h2>
      <div className="moodboards-grid">
        {MOODBOARDS.map((board) => (
          <div className="moodboard-card" key={board.title}>
            <div
              className="collage"
              onClick={() => openLightbox(board.title, board.lightbox)}
            >
              {board.collage.map((src, i) => (
                <img key={src} src={src} alt={`${board.alt} ${i + 1}`} />
              ))}
            </div>
            <h3>{board.label}</h3>
          </div>
        ))}
      </div>
    </div>
  );
}
