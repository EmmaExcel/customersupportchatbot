import { Link } from 'react-router-dom'

export default function PrivacyPage() {
  return (
    <div className="page">
      <main className="legal-page">
        <p><Link to="/">Back to the demo</Link></p>
        <h1>Privacy Policy</h1>
        <p className="legal-date">Last updated: September 18, 2026</p>

        <h2>Data we collect</h2>
        <p>
          When you use this support chat, we collect the messages you send, the
          replies you receive, and the account identifier you use for support
          actions. If you ask the assistant to place an order, we collect the
          items and shipping details needed to complete that order.
        </p>

        <h2>How we use your data</h2>
        <p>
          We use your messages to answer your question, look up your account,
          and carry out the actions you approve, such as placing an order. We
          keep a record of support conversations so we can review and improve
          the service.
        </p>

        <h2>Service providers</h2>
        <p>
          We use a third party language model provider to generate assistant
          replies. Messages are sent to that provider only to produce a reply.
          We do not sell your data and we do not use your support messages for
          advertising.
        </p>

        <h2>Data storage</h2>
        <p>
          Conversation records and order data are stored in our database. You
          can ask us to delete your support history by writing to
          privacy@example.com. We process deletion requests within 30 days.
        </p>

        <h2>Your rights</h2>
        <p>
          You can request a copy of the data we hold about you, ask us to
          correct it, or ask us to delete it. To make a request, write to
          privacy@example.com.
        </p>

        <h2>Contact</h2>
        <p>
          Questions about this policy can be sent to privacy@example.com.
        </p>
      </main>
    </div>
  )
}
