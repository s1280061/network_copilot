declare module "katex/contrib/auto-render" {
  interface RenderMathDelimiter {
    left: string;
    right: string;
    display: boolean;
  }
  interface RenderMathOptions {
    delimiters?: RenderMathDelimiter[];
    ignoredTags?: string[];
    ignoredClasses?: string[];
    throwOnError?: boolean;
    errorCallback?: (msg: string, err: Error) => void;
    macros?: Record<string, string>;
  }
  export default function renderMathInElement(
    elem: HTMLElement,
    options?: RenderMathOptions
  ): void;
}
