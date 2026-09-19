import { Link } from 'react-router-dom'
import { howItWorks, projectPage, sections, stack, toolCards } from '../content.js'

export default function ProjectPage() {
  return (
    <div className="page">
      <main>
        <section className="project-header">
          <p><Link to="/">{projectPage.backToDemo}</Link></p>
          <h1>{projectPage.title}</h1>
          {projectPage.intro.map((paragraph) => (
            <p key={paragraph}>{paragraph}</p>
          ))}
        </section>

        <section className="showcase">
          <h2>{sections.capabilities}</h2>
          <div className="capability-grid">
            {toolCards.map((card) => (
              <article key={card.name} className="capability-card">
                <code className="tool-name">{card.name}</code>
                <h3>{card.title}</h3>
                <p>{card.description}</p>
                <p className="card-example">Try: {card.example}</p>
                <p className="card-source">{card.source}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="showcase">
          <h2>{sections.howItWorks}</h2>
          <ol className="step-list">
            {howItWorks.map((item) => (
              <li key={item.step}>
                <span className="step-number">{item.step}</span>
                <div>
                  <h3>{item.title}</h3>
                  <p>{item.text}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        <section className="showcase">
          <h2>{sections.stack}</h2>
          <ul className="stack-list">
            {stack.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
      </main>
    </div>
  )
}
