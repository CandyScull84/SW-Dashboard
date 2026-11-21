import { useEffect, useState } from 'react';
import Header from './components/Header';
// import MembersPanel from './components/MembersPanel'; lägg till om Memberspanel ska tillbaka
import "@fontsource/material-symbols-outlined";
import FailingPipelinesIndicator from './components/FailingPipelinesIndicator';
import Carousel from './components/Carousel'; 
import MergeDropdown from './components/MergeDropdown';
import './App.css';
import QuickInfoPanel from './components/QuickInfoPanel';
// import useAutoRefresh from './hooks/useAutoRefresh';
import useDashboardData from './hooks/useDashboardData';



export default function App() {
  const {
    members, pipelines, merges, projects, pushes, loading, error
  } = useDashboardData();
  
  const globalLoading = loading;

  // const autoScroll = true;
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem("darkMode") === "true";
  });
  const [autoScroll, setAutoScroll] = useState(() => {
    return localStorage.getItem("autoScroll") === "true"
  });

  // Mockdata for carousel
  // const  testItems = [
  //   { title: "Merge Request #1", description: "Fix login-bugg i auth-service"},
  //   { title: "Commit i UI-lib", description: "Refaktor av knappar"},
  //   { title: "Push i reporting-tool", description: "Lagt till månadsrapport"},
  //   { title: "Merge Request #2", description: "Uppdaterat CI/CD-pipeline"},
  // ];

  // const carouselItems = [
  //   {
  //     title: "Merge Requests",
  //     description: " ",
  //     type: "merge",
  //     data: merges,
  //   }
  // ];

  //Only debugging
  useEffect(() => {
      console.log("Loaded team members:", members.length);
  }, [members]);

  useEffect(() => {
      console.log("Number of failing pipelines:", pipelines.length);
  }, [pipelines]);

    useEffect(() =>{
    console.log("Push events updated:", pushes.length);
  }, [pushes]);

  useEffect(() => {
    localStorage.setItem("darkMode", darkMode);
  }, [darkMode]);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
      document.documentElement.classList.remove("light");
    } else {
      document.documentElement.classList.add("light");
      document.documentElement.classList.remove("dark");
    }
  }, [darkMode]);

      useEffect(() => {
    localStorage.setItem("autoScroll", autoScroll);
  }, [autoScroll]);

  return (
    <>
      <div className="dashboard">
        <Header
          title="SW Dashboard"
          rightSlot={
            <>
            <div className="header__toggles">
              <button
                className="toggle__btn"
                onClick={() => setDarkMode(prev => !prev)}
                title="Toggle dark/light mode"
              >
                <span className="material-symbols-outlined">
                  {darkMode ? "dark_mode" : "light_mode"}
                </span>
              </button>

              <button
                className="toggle__btn"
                onClick={() => setAutoScroll(prev => !prev)}
                title="Toggle auto-scroll"
              >
                <span className="material-symbols-outlined">
                  {autoScroll ? "autoplay" : "pause_circle"}
                </span>
              </button>
            </div>
            {/* NO MR Indicator*/}
            {merges.length === 0 && (
              <div className="mr__indicator mr--none">
                <span>NO MR</span>
              </div>
            )}
            {/* NO FP Indicator*/}
            {pipelines.length === 0 ? (
              <FailingPipelinesIndicator pipelines={pipelines} compact />
            ) : null
            }
          </>
          }
        />

        <div className="dashboard__content">
          <div className="dashboard__sidebar">
            {globalLoading ? (
              <div className="global-spinner" title="Updating data..."></div>
            ) : (
              <div className="global-dot" ></div>
              )}
            <QuickInfoPanel />
            {/* <MembersPanel members={members} loadingMembers={loadingMembers} autoScroll={autoScroll}/>
            {error && <p className="error-text">Error fetchin data: {error.message}</p>} */}
          </div>
        
          <main className="dashboard__main">
            <div className="dashboard__toprow">
              <div className="toprow__left">
                <MergeDropdown merges={merges} autoScroll={autoScroll} />
              </div>

              {/* <div className="toprow__center">
                <ActiveProjectsDonut projects={projects} loading={loadingProjects} error={errorProjects} />
              </div>*/}

              <div className="toprow__right">
                {pipelines.length > 0  && (
                  <FailingPipelinesIndicator pipelines={pipelines} autoScroll={autoScroll}/>
                )}
              </div>
            </div>
            {/* Carousel */}
            <Carousel 
              projects={projects} 
              pushes={pushes}
              members={members} 
              autoScroll={autoScroll}
              />
            
          </main>
        </div>
      </div>
    </>
  )
};