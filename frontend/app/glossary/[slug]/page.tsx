import ArticleView from "@/components/article/ArticleView";

export default function ArticlePage({ params }: { params: { slug: string } }) {
  return <ArticleView slug={params.slug} />;
}
