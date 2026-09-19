import { Link } from 'react-router-dom'
import ChatWidget from './components/ChatWidget.jsx'
import { demo, project, projectPage } from './content.js'

export default function App() {
  return (
    <div className="page">
      <main>
        <section className="project-header">
          <h1>{project.name}</h1>
          <p>{project.description}</p>
          <p><Link to="/project">Read the full project overview</Link></p>
        </section>

        <section className="demo-section">
          {/* <h2>{demo.title}</h2> */}
          <p>{demo.intro}</p>
          <div className="chat-panel" aria-label="Chat with the demo assistant">
            <ChatWidget examplePrompts={demo.prompts} />
          </div>
        </section>
      </main>
    </div>
  )
}
