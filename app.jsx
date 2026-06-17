const { useState, useEffect, useRef } = React;

function App() {
  const [selectedModule, setSelectedModule] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedPath, setSelectedPath] = useState(null);
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

  const pathModules = selectedPath
    ? window.MODULES.filter(m => window.LEARNING_PATH[selectedPath].modules.includes(m.id))
    : null;

  return (
    <div className="app">
      <Header theme={theme} toggleTheme={toggleTheme} />

      <main className="main-content">
        <Hero />

        <section className="search-section">
          <div className="container">
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
          </div>
        </section>

        <section className="learning-paths">
          <div className="container">
            <h2>Choose Your Learning Path</h2>
            <div className="paths-grid">
              {Object.keys(window.LEARNING_PATH).map(key => {
                const path = window.LEARNING_PATH[key];
                return (
                  <button
                    key={key}
                    className={`path-card ${selectedPath === key ? 'active' : ''}`}
                    onClick={() => setSelectedPath(selectedPath === key ? null : key)}
                  >
                    <h3>{path.title}</h3>
                    <p>{path.description}</p>
                    <div className="path-meta">
                      <span className="badge">{path.modules.length} modules</span>
                      <span className="badge">{path.estimatedWeeks}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </section>

        <section className="modules-section">
          <div className="container">
            <h2>
              {selectedPath
                ? `${window.LEARNING_PATH[selectedPath].title} Modules`
                : "All Course Modules"}
            </h2>
            <div className="modules-grid">
              {(pathModules || filteredModules).map(module => (
                <ModuleCard
                  key={module.id}
                  module={module}
                  isSelected={selectedModule?.id === module.id}
                  onClick={() => setSelectedModule(
                    selectedModule?.id === module.id ? null : module
                  )}
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
            <svg viewBox="0 0 40 40" className="logo-icon">
              <defs>
                <linearGradient id="logo-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#6366f1" />
                  <stop offset="50%" stopColor="#8b5cf6" />
                  <stop offset="100%" stopColor="#d946ef" />
                </linearGradient>
              </defs>
              <rect width="40" height="40" rx="8" fill="url(#logo-gradient)" />
              <text x="20" y="28" textAnchor="middle" fill="white" fontSize="20" fontWeight="bold">A</text>
            </svg>
            <div className="logo-text">
              <h1>Agentic AI Fundamentals</h1>
              <p>From Python to Production AI Systems</p>
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
            Master Agentic AI Development
          </h2>
          <p className="hero-subtitle">
            Learn to build production-ready AI agents from scratch.
            15 comprehensive modules covering Python, LLMs, RAG, multi-agent systems, and deployment.
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
        {isSelected ? 'Hide Videos' : 'View Videos'}
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <polyline points={isSelected ? "18 15 12 9 6 15" : "6 9 12 15 18 9"}></polyline>
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
  }, []);

  return (
    <section className="video-list-section" ref={listRef}>
      <div className="container">
        <div className="video-list-header">
          <div>
            <h2>{module.title}</h2>
            <p>{module.videoCount} videos · {module.duration}</p>
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

  return (
    <div className={`video-card ${isPlaceholder ? 'placeholder' : ''}`}>
      <div className={`video-thumbnail color-${moduleColor}`}>
        <div className="video-number">{index}</div>
        {isPlaceholder ? (
          <div className="coming-soon">Coming Soon</div>
        ) : (
          <svg className="play-icon" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
        )}
      </div>
      <div className="video-info">
        <h4 className="video-title">{video.title}</h4>
        <p className="video-description">{video.description}</p>
        <div className="video-meta">
          <span className="duration">{video.duration}</span>
          {!isPlaceholder && (
            <a
              href={video.url}
              target="_blank"
              rel="noopener noreferrer"
              className="watch-button"
            >
              Watch
            </a>
          )}
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
        <div className="footer-content">
          <div className="footer-section">
            <h3>Agentic AI Fundamentals</h3>
            <p>
              A comprehensive learning path from Python basics to production-ready
              AI agents. All content available for free on YouTube.
            </p>
          </div>

          <div className="footer-section">
            <h4>Connect</h4>
            <a
              href="https://youtube.com/@AgenticAIFundamentals"
              target="_blank"
              rel="noopener noreferrer"
              className="footer-link"
            >
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
              </svg>
              @AgenticAIFundamentals
            </a>
          </div>

          <div className="footer-section">
            <h4>Resources</h4>
            <a href="https://github.com/kakatur/agentic-ai-fundamentals" className="footer-link">
              GitHub Repository
            </a>
          </div>
        </div>

        <div className="footer-bottom">
          <p>&copy; 2026 Agentic AI Fundamentals. All rights reserved.</p>
          <p>Built with React · Hosted on GitHub Pages</p>
        </div>
      </div>
    </footer>
  );
}

ReactDOM.render(<App />, document.getElementById("root"));
