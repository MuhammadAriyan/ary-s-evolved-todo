# ChatKit Theming Skill

## Purpose
Apply glass theme styling to OpenAI ChatKit components for the AI Todo Chatbot interface.

## Context7 Reference
- Library: `/openai/openai-chatkit`
- Query: "custom theming CSS overrides"

## Glass Theme Design System

### 1. Core Glass Variables
```css
/* frontend/app/globals.css */
:root {
  /* Glass backgrounds */
  --glass-bg: rgba(0, 0, 0, 0.3);
  --glass-bg-light: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.1);

  /* Aura colors */
  --aura-purple: #a855f7;
  --aura-purple-light: rgba(168, 85, 247, 0.2);
  --aura-cyan: #22d3ee;
  --aura-cyan-light: rgba(34, 211, 238, 0.2);

  /* Text colors */
  --text-primary: rgba(255, 255, 255, 0.95);
  --text-secondary: rgba(255, 255, 255, 0.7);
  --text-muted: rgba(255, 255, 255, 0.5);

  /* Blur values */
  --blur-sm: 8px;
  --blur-md: 12px;
  --blur-xl: 24px;
}
```

### 2. Chat Container Styling
```tsx
// frontend/app/(protected)/chat/components/ChatContainer.tsx
export function ChatContainer({ children }: { children: React.ReactNode }) {
  return (
    <div className="
      h-full w-full
      bg-black/30
      backdrop-blur-xl
      border border-white/10
      rounded-2xl
      overflow-hidden
      shadow-2xl
      shadow-black/50
    ">
      {children}
    </div>
  );
}
```

### 3. Message Bubble Styles
```tsx
// frontend/app/(protected)/chat/components/MessageBubble.tsx
interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
  agentName?: string;
  agentIcon?: string;
}

export function MessageBubble({ role, content, agentName, agentIcon }: MessageBubbleProps) {
  const isUser = role === 'user';

  return (
    <div className={`
      flex ${isUser ? 'justify-end' : 'justify-start'}
      mb-4
    `}>
      <div className={`
        max-w-[80%] p-4 rounded-2xl
        ${isUser
          ? 'bg-aura-purple/20 border border-aura-purple/30 text-white'
          : 'bg-white/5 border border-white/10 text-white/90'
        }
        backdrop-blur-sm
      `}>
        {!isUser && agentName && (
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xl">{agentIcon}</span>
            <span className="text-xs text-white/50 font-medium">{agentName}</span>
          </div>
        )}
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
      </div>
    </div>
  );
}
```

### 4. Input Area Styling
```tsx
// frontend/app/(protected)/chat/components/ChatInput.tsx
export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('');

  return (
    <div className="
      p-4
      border-t border-white/10
      bg-black/20
      backdrop-blur-md
    ">
      <div className="
        flex items-center gap-3
        bg-black/30
        border border-white/20
        rounded-xl
        p-2
        focus-within:border-aura-purple/50
        transition-colors
      ">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type a message..."
          className="
            flex-1
            bg-transparent
            text-white
            placeholder:text-white/30
            outline-none
            px-3 py-2
          "
          disabled={disabled}
        />
        <VoiceInputButton />
        <button
          onClick={() => onSend(message)}
          disabled={disabled || !message.trim()}
          className="
            p-2 rounded-lg
            bg-aura-purple/20
            hover:bg-aura-purple/30
            disabled:opacity-50
            disabled:cursor-not-allowed
            transition-colors
          "
        >
          <SendIcon className="w-5 h-5 text-aura-purple" />
        </button>
      </div>
    </div>
  );
}
```

### 5. Conversation Sidebar
```tsx
// frontend/app/(protected)/chat/components/ConversationList.tsx
export function ConversationList({ conversations, activeId, onSelect }: Props) {
  return (
    <div className="
      w-64
      h-full
      bg-black/40
      backdrop-blur-xl
      border-r border-white/10
      overflow-y-auto
    ">
      <div className="p-4 border-b border-white/10">
        <button className="
          w-full p-3 rounded-xl
          bg-aura-purple/20
          hover:bg-aura-purple/30
          border border-aura-purple/30
          text-white text-sm font-medium
          transition-colors
        ">
          + New Conversation
        </button>
      </div>

      <div className="p-2">
        {conversations.map((conv) => (
          <button
            key={conv.id}
            onClick={() => onSelect(conv.id)}
            className={`
              w-full p-3 rounded-xl mb-1
              text-left text-sm
              transition-colors
              ${activeId === conv.id
                ? 'bg-white/10 text-white'
                : 'text-white/70 hover:bg-white/5 hover:text-white'
              }
            `}
          >
            <p className="truncate font-medium">
              {conv.title || 'New Conversation'}
            </p>
            <p className="text-xs text-white/40 mt-1">
              {formatDate(conv.updatedAt)}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
}
```

### 6. Loading States
```tsx
// Typing indicator with glass styling
export function TypingIndicator({ agentName, agentIcon }: Props) {
  return (
    <div className="
      flex items-center gap-3
      p-4 rounded-2xl
      bg-white/5
      border border-white/10
      backdrop-blur-sm
      max-w-[200px]
    ">
      <span className="text-xl">{agentIcon}</span>
      <div className="flex gap-1">
        <span className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <span className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <span className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  );
}
```

## Tailwind Config Extensions
```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'aura-purple': '#a855f7',
        'aura-cyan': '#22d3ee',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
};
```

## Key Principles
- **Consistent Glass Effect**: bg-black/30 + backdrop-blur-xl + border-white/10
- **Aura Accents**: Purple for user actions, cyan for highlights
- **Subtle Borders**: white/10 to white/20 for depth
- **Readable Text**: white/90 for primary, white/50 for muted
- **Smooth Transitions**: All interactive elements have transition-colors
