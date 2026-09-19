export const project = {
  name: 'Customer Support Chatbot',
  description:
    'A proof of concept support assistant. The browser sends a message to a FastAPI backend, the language model chooses an MCP tool through function calling, and that tool reads or writes data in Turso SQLite.',
}

export const demo = {
  title: 'Live demo',
  intro:
    'Use the example prompts to exercise each tool. The assistant never invents product or account data, and orders are only placed after you confirm.',
  prompts: [
    'Do you have the KB-101 keyboard in stock?',
    'Show my recent orders.',
    'What is the price of the Monitor 27 QHD?',
    'Order one USB-C Hub 7 in 1 to 48 Market Street, San Francisco, CA 94103.',
  ],
}

export const projectPage = {
  title: 'Project overview',
  backToDemo: 'Back to the demo',
  intro: [
    'This project is a proof of concept customer support chatbot. It shows how a language model can be connected to real business data and real write operations through the Model Context Protocol.',
    'The frontend is a React chat built with Vite. Messages stream from a FastAPI backend, which uses the OpenAI SDK with function calling. The model is DeepSeek by default, and the same code works with any OpenAI-compatible provider.',
    'When the model decides a tool is needed, the backend opens a streamable HTTP session to a separate MCP server. That server exposes three tools: get_product_details, get_user_data, and place_order.',
    'The MCP server is the only component that touches the database. It validates inputs, checks stock before ordering, and writes orders and order items in a single transaction. Data lives in Turso, a hosted SQLite database, with a local file fallback for development.',
    'The assistant is instructed never to invent product details, prices, stock levels, user data, or order numbers. It confirms items and shipping details before calling place_order.',
  ],
}

export const sections = {
  capabilities: 'What it can do',
  howItWorks: 'How it works',
  stack: 'Built with',
}

export const toolCards = [
  {
    name: 'get_product_details',
    title: 'Product lookup',
    description: 'Searches products by SKU or id and returns the name, price, stock level, and category.',
    example: 'Do you have the KB-101 keyboard in stock?',
    source: 'MCP tool reading from Turso SQLite',
  },
  {
    name: 'get_user_data',
    title: 'Account and order history',
    description: 'Loads the signed in user profile and the ten most recent orders for that user.',
    example: 'Show my recent orders.',
    source: 'MCP tool reading from Turso SQLite',
  },
  {
    name: 'place_order',
    title: 'Order placement',
    description: 'Validates stock, writes the order and its items in a transaction, and returns an order number.',
    example: 'Order one USB-C Hub 7 in 1 to 48 Market Street, San Francisco, CA 94103.',
    source: 'MCP tool writing to Turso SQLite',
  },
]

export const howItWorks = [
  {
    step: '1',
    title: 'React chat interface',
    text: 'The message is sent from the browser to the FastAPI backend over a streaming endpoint.',
  },
  {
    step: '2',
    title: 'LLM tool selection',
    text: 'DeepSeek decides which MCP tool to call, or asks the customer for missing details before acting.',
  },
  {
    step: '3',
    title: 'MCP client',
    text: 'The backend opens a streamable HTTP session to the MCP server only when a tool is needed.',
  },
  {
    step: '4',
    title: 'MCP server',
    text: 'The tool validates its inputs, reads or writes data, and returns a structured JSON result.',
  },
  {
    step: '5',
    title: 'Turso SQLite',
    text: 'Products, users, orders, and conversation history are stored in a hosted SQLite database.',
  },
]

export const stack = [
  'Python',
  'FastAPI',
  'OpenAI SDK with function calling',
  'DeepSeek',
  'MCP streamable HTTP',
  'Turso SQLite',
  'Vite',
  'React',
]
