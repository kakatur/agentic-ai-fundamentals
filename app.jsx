const { useState, useEffect, useRef } = React;

function App() {
  const [selectedModule, setSelectedModule] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [theme, setTheme] = useState("dark");

  useEffect(() => {
    const savedTheme = localStorage.getItem("agentic-ai-theme") || "dark";
    setTheme(savedTheme);
    document.documentElement.dataset.theme = savedTheme;
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === "dark" ? "light" : "dark";
    setTheme(newTheme);
    document.documentElement.dataset.theme = newTheme;
    localStorage.setItem("agentic-ai-theme", newTheme);
  };

  const filteredModules = window.MODULES.filter(module => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      module.title.toLowerCase().includes(query) ||
      module.description.toLowerCase().includes(query) ||
      module.videos.some(v =>
        v.title.toLowerCase().includes(query) ||
        v.description.toLowerCase().includes(query)
      )
    );
  });

  const showModuleVideos = (module) => {
    setSelectedModule(module);
    if (selectedModule?.id === module.id) {
      requestAnimationFrame(() => {
        document
          .querySelector(".video-list-section")
          ?.scrollIntoView({ behavior: "smooth", block: "nearest" });
      });
    }
  };

  return (
    <div className="app">
      <Header theme={theme} toggleTheme={toggleTheme} />

      <main className="main-content">
        <Hero />
        <InstructorSection />

        <section className="modules-section">
          <div className="container">
            <h2>Course Modules</h2>
            <div className="search-bar">
              <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.35-4.35"></path>
              </svg>
              <input
                type="text"
                placeholder="Search modules or videos..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="modules-grid">
              {filteredModules.map(module => (
                <ModuleCard
                  key={module.id}
                  module={module}
                  isSelected={selectedModule?.id === module.id}
                  onClick={() => showModuleVideos(module)}
                />
              ))}
            </div>
          </div>
        </section>

        {selectedModule && (
          <VideoList module={selectedModule} onClose={() => setSelectedModule(null)} />
        )}

        <ProjectsSection />
        <ResourcesSection />
        <Footer />
      </main>
    </div>
  );
}

function Header({ theme, toggleTheme }) {
  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <div className="logo">
            <img
              src="assets/brand/youtube-channel-profile-1024x1024.png"
              alt=""
              className="logo-icon"
            />
            <div className="logo-text">
              <h1>Agentic AI Fundamentals</h1>
              <p>Concepts. Code Samples. Interview Questions.</p>
            </div>
          </div>

          <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === "dark" ? (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
              </svg>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="hero">
      <div className="container">
        <div className="hero-content">
          <h2 className="hero-title">
            Agentic AI Fundamentals
          </h2>
          <p className="hero-subtitle">
            A complete learning path from Python fundamentals to building production-ready AI agents.
            All content is available for free on YouTube, with accompanying source code and lesson notes on GitHub.
          </p>
          <div className="hero-stats">
            <div className="stat">
              <div className="stat-value">{window.MODULES.length}</div>
              <div className="stat-label">Modules</div>
            </div>
            <div className="stat">
              <div className="stat-value">
                {window.MODULES.reduce((sum, m) => sum + m.videoCount, 0)}
              </div>
              <div className="stat-label">Videos</div>
            </div>
            <div className="stat">
              <div className="stat-value">
                {Math.round(window.MODULES.reduce((sum, m) =>
                  sum + parseFloat(m.duration.replace(/[^\d.]/g, '')), 0)
                )}h
              </div>
              <div className="stat-label">Content</div>
            </div>
          </div>
          <div className="hero-actions">
            <a
              href="https://youtube.com/@AgenticAIFundamentals"
              target="_blank"
              rel="noopener noreferrer"
              className="cta-button"
            >
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
              </svg>
              Subscribe on YouTube
            </a>
            <a
              href="https://github.com/kakatur/agentic-ai-fundamentals"
              target="_blank"
              rel="noopener noreferrer"
              className="cta-button cta-button-secondary"
            >
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/>
              </svg>
              View on GitHub
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

function InstructorSection() {
  return (
    <section className="instructor-intro">
      <div className="container">
        <div className="instructor-card-compact">
          <div className="instructor-info">
            <h3 className="instructor-name">Krishna Kakatur</h3>
            <p className="instructor-bio">
              As a Data and Agentic AI leader, I build platforms that make trusted data accessible across organizations.
              I've led the strategy, design, and implementation of modern data, AI, and analytics platforms at scale.
              My focus is on creating reliable, governed ecosystems where teams own their data and leverage self-service
              capabilities to unlock value through intelligent automation and agentic AI solutions.
            </p>
            <div className="instructor-links">
              <a href="https://www.linkedin.com/in/kkakatur/" target="_blank" rel="noopener noreferrer" className="social-link">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20.5 2h-17A1.5 1.5 0 002 3.5v17A1.5 1.5 0 003.5 22h17a1.5 1.5 0 001.5-1.5v-17A1.5 1.5 0 0020.5 2zM8 19H5v-9h3zM6.5 8.25A1.75 1.75 0 118.3 6.5a1.78 1.78 0 01-1.8 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93A1.74 1.74 0 0013 14.19a.66.66 0 000 .14V19h-3v-9h2.9v1.3a3.11 3.11 0 012.7-1.4c1.55 0 3.36.86 3.36 3.66z"></path>
                </svg>
                LinkedIn
              </a>
              <a href="https://github.com/kakatur" target="_blank" rel="noopener noreferrer" className="social-link">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2A10 10 0 002 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0012 2z"></path>
                </svg>
                GitHub
              </a>
              <a href="https://medium.com/@kakatur" target="_blank" rel="noopener noreferrer" className="social-link">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M13.54 12a6.8 6.8 0 01-6.77 6.82A6.8 6.8 0 010 12a6.8 6.8 0 016.77-6.82A6.8 6.8 0 0113.54 12zM20.96 12c0 3.54-1.51 6.42-3.38 6.42-1.87 0-3.39-2.88-3.39-6.42s1.52-6.42 3.39-6.42 3.38 2.88 3.38 6.42M24 12c0 3.17-.53 5.75-1.19 5.75-.66 0-1.19-2.58-1.19-5.75s.53-5.75 1.19-5.75C23.47 6.25 24 8.83 24 12z"></path>
                </svg>
                Medium
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function ModuleCard({ module, isSelected, onClick }) {
  return (
    <div
      className={`module-card color-${module.color} ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <div className="module-header">
        <div className="module-number">Module {module.id}</div>
        <div className={`module-badge color-${module.color}`}>
          {module.videoCount} videos
        </div>
      </div>
      <h3 className="module-title">{module.title}</h3>
      <p className="module-description">{module.description}</p>
      <div className="module-meta">
        <span className="duration">{module.duration}</span>
      </div>
      <button className="module-action">
        View Videos
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </button>
    </div>
  );
}

function VideoList({ module, onClose }) {
  const listRef = useRef(null);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [module.id]);

  return (
    <section className="video-list-section" ref={listRef}>
      <div className="container">
        <div className="video-list-header">
          <div>
            <h2>{module.title}</h2>
            <p>{module.videoCount} videos · {module.duration}</p>
            {module.playlistUrl && (
              <a
                href={module.playlistUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="playlist-link"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M4 6h12v2H4V6zm0 5h12v2H4v-2zm0 5h8v2H4v-2zm14.5-4.5L22 14l-3.5 2.5v-5z"/>
                </svg>
                Watch playlist
              </a>
            )}
          </div>
          <button className="close-button" onClick={onClose}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <div className="videos-grid">
          {module.videos.map((video, idx) => (
            <VideoCard key={idx} video={video} index={idx + 1} moduleColor={module.color} />
          ))}
        </div>
      </div>
    </section>
  );
}

function VideoCard({ video, index, moduleColor }) {
  const isPlaceholder = video.url === "PLACEHOLDER";
  const thumbnailContent = (
    <>
      {video.thumbnailUrl && (
        <img
          src={video.thumbnailUrl}
          alt=""
          className="video-thumbnail-image"
          loading="lazy"
        />
      )}
      <div className="video-number">{index}</div>
      {isPlaceholder ? (
        <div className="coming-soon">Coming Soon</div>
      ) : (
        <div className="play-icon-background" aria-hidden="true">
          <svg className="play-icon" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
        </div>
      )}
    </>
  );

  return (
    <div className={`video-card ${isPlaceholder ? 'placeholder' : ''}`}>
      {isPlaceholder ? (
        <div className={`video-thumbnail color-${moduleColor}`}>
          {thumbnailContent}
        </div>
      ) : (
        <a
          href={video.url}
          target="_blank"
          rel="noopener noreferrer"
          className={`video-thumbnail video-thumbnail-link color-${moduleColor}`}
          aria-label={`Watch ${video.title}`}
        >
          {thumbnailContent}
        </a>
      )}
      <div className="video-info">
        <h4 className="video-title">{video.title}</h4>
        <p className="video-description">{video.description}</p>
        <div className="video-meta">
          <span className="duration">{video.duration}</span>
        </div>
      </div>
    </div>
  );
}

function ProjectsSection() {
  const [selectedDifficulty, setSelectedDifficulty] = useState("Beginner");

  const currentProjects = window.PROJECT_TEMPLATES.find(
    p => p.difficulty === selectedDifficulty
  );

  return (
    <section className="projects-section">
      <div className="container">
        <h2>Hands-On Projects</h2>
        <p className="section-subtitle">
          Apply your knowledge with real-world projects at every skill level
        </p>

        <div className="difficulty-tabs">
          {window.PROJECT_TEMPLATES.map(template => (
            <button
              key={template.difficulty}
              className={`tab ${selectedDifficulty === template.difficulty ? 'active' : ''}`}
              onClick={() => setSelectedDifficulty(template.difficulty)}
            >
              {template.difficulty}
            </button>
          ))}
        </div>

        <div className="projects-grid">
          {currentProjects?.projects.map((project, idx) => (
            <div key={idx} className="project-card">
              <h3>{project.name}</h3>
              <p>{project.description}</p>
              <div className="project-skills">
                {project.skills.map((skill, i) => (
                  <span key={i} className="skill-tag">{skill}</span>
                ))}
              </div>
              <div className="project-meta">
                <span className="time-estimate">{project.estimatedTime}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function ResourcesSection() {
  return (
    <section className="resources-section">
      <div className="container">
        <h2>Additional Resources</h2>
        <div className="resources-grid">
          {window.RESOURCES.map((category, idx) => (
            <div key={idx} className="resource-category">
              <h3>{category.category}</h3>
              <ul>
                {category.items.map((item, i) => (
                  <li key={i}>
                    <a href={item.url} target="_blank" rel="noopener noreferrer">
                      {item.name}
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                        <polyline points="15 3 21 3 21 9"></polyline>
                        <line x1="10" y1="14" x2="21" y2="3"></line>
                      </svg>
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-bottom">
          <p>&copy; 2026 Agentic AI Fundamentals. All rights reserved.</p>
          <p>Built with React · Hosted on GitHub Pages</p>
        </div>
      </div>
    </footer>
  );
}

ReactDOM.render(<App />, document.getElementById("root"));
