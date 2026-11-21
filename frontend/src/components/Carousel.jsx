import { useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";
import "./Carousel.css";
import ProjectListCard from "./cards/ProjectListCard";
import PushListCard from "./cards/PushListCard";
import useAutoScroll from "../hooks/useAutoScroll";


export default function Carousel({
  projects,
  // loadingProjects,
  // errorProjects,
  pushes,
  // loadingPushes,
  // errorPushes,
  members,
  autoScroll,
}) {
  console.log("Carousel received projects", projects);

  const trackRef = useRef(null);
  const [isSliding, setIsSliding] = useState(false);
 
  // const contentDebugRef = useRef(null);
  const slideDuration = 1500; // time for movement (ms)
  const pauseDuration = 10000; // time standstill (ms)
  const cardWidth = 50; // % of wrapper per card

  const pushesWithAvatars = pushes?.map(p => {
    const match = members?.find(
      m =>
        m.name?.toLowerCase() === p.user_name?.toLowerCase() ||
      m.username?.toLowerCase() === p.user_name?.toLowerCase()
    );
    return {
      ...p,
      avatar_url: match?.avatar_url || p.avatar_url || null,
    };
  }) || [];

 const slides = [
  {
    key: "recent-pushes",
    title: "Recent Pushes",
    content: 
      <PushListCard pushes={pushesWithAvatars} autoScroll={autoScroll}/>
  
  },
  {
    key: "active-projects",
    title: "Activity in projects",
    content: 
      <ProjectListCard projects={projects} autoScroll={autoScroll}/>
    
  },
 ];
  const loopedItems = [...slides, ...slides];

  const scrollRefs = [
    useAutoScroll(autoScroll),
    useAutoScroll(autoScroll),
    useAutoScroll(autoScroll),
    useAutoScroll(autoScroll),
  ];
  // useEffect(() => {
  //   if (contentDebugRef.current) {
  //     console.log(
  //       "Carousel COntent height:",
  //       contentDebugRef.current.clientHeight,
  //       "scroll:",
  //       contentDebugRef.current.scrollHeight
  //     );
  //   }
  // }, [projects, pushes])

  useEffect(() => {
    console.log(" Carousel data changed, trig autoscroll");
  }, [projects, pushes]);
  
  useEffect(() => {
    if (!trackRef.current) return;
    let timeout;

    const runSlide = () => {
      if (isSliding) return;

      setIsSliding(true);
      const track = trackRef.current;
      track.style.transition = `transform ${slideDuration}ms ease-in-out`;
      track.style.transform = `translateX(-${cardWidth}%)`;

      // after animation: move first card last and clear transform
      setTimeout(() => {
        track.style.transition = "none";
        track.appendChild(track.firstElementChild);
        track.style.transform = "translateX(0)";
        setIsSliding(false);
      }, slideDuration);

      // start next cycle
      timeout = setTimeout(runSlide, slideDuration + pauseDuration);
    };

    timeout = setTimeout(runSlide, pauseDuration);
    return () => clearTimeout(timeout);
  }, [isSliding]);

  const handleManual = (dir) => {
    if (isSliding) return;
    const track = trackRef.current;
    const first = track.firstElementChild;
    const last = track.lastElementChild;

    setIsSliding(true);
    track.style.transition = `transform ${slideDuration}ms ease-in-out`;
    track.style.transform = `translateX(${dir === "next" ? -cardWidth : cardWidth}%)`;

    setTimeout(() => {
      track.style.transition = "none";
      if (dir === "next") track.appendChild(first);
      else track.insertBefore(last, first);
      track.style.transform = "translateX(0)";
      setIsSliding(false);
    }, slideDuration);
  };

  return (
    <div className="carousel__wrapper">
      <div className="carousel__track" ref={trackRef}>
        {loopedItems.map((item, i) => (
          <div key={`${item.key}-${i}`} className="carousel__card">
            <h3 className="carousel__title">{item.title}</h3>
            <div className="carousel__content" ref={scrollRefs[i]}>{item.content}</div>
          </div>
        ))}
      </div>

      <button
        className="carousel__btn prev"
        onClick={() => handleManual("prev")}
      >
        &lt;
      </button>
      <button
        className="carousel__btn next"
        onClick={() => handleManual("next")}
      >
        &gt;
      </button>
    </div>
  );
}

Carousel.propTypes = {
  projects: PropTypes.array,
  pushes: PropTypes.array,
  members: PropTypes.array,
  autoScroll: PropTypes.bool,
};

