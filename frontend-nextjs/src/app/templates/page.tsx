import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Search, 
  Plus,
  Copy,
  Edit,
  Trash2,
  Play,
  Download,
  Star,
  StarOff,
  Globe,
  ShoppingBag,
  Newspaper,
  Building,
  Users,
  MoreHorizontal,
  Eye,
  Settings
} from "lucide-react";
import { useState } from "react";

// Mock template data
const mockTemplates = [
  {
    id: "template_001",
    name: "E-commerce Product Scraper",
    description: "Comprehensive product data extraction with prices, reviews, and inventory",
    category: "E-commerce",
    icon: ShoppingBag,
    isStarred: true,
    isPublic: true,
    author: "System",
    lastModified: "2024-01-14",
    usageCount: 1247,
    successRate: 98.5,
    fields: ["title", "price", "description", "images", "reviews", "stock"],
    tags: ["products", "prices", "inventory"],
    complexity: "intermediate"
  },
  {
    id: "template_002", 
    name: "News Article Extractor",
    description: "Extract articles with metadata, content, and author information",
    category: "Content",
    icon: Newspaper,
    isStarred: false,
    isPublic: true,
    author: "Community",
    lastModified: "2024-01-13",
    usageCount: 856,
    successRate: 96.2,
    fields: ["headline", "content", "author", "publish_date", "tags"],
    tags: ["news", "articles", "content"],
    complexity: "beginner"
  },
  {
    id: "template_003",
    name: "Real Estate Listings",
    description: "Property listings with prices, features, and contact information",
    category: "Real Estate",
    icon: Building,
    isStarred: true,
    isPublic: false,
    author: "You",
    lastModified: "2024-01-15",
    usageCount: 423,
    successRate: 94.8,
    fields: ["address", "price", "bedrooms", "bathrooms", "square_feet", "agent"],
    tags: ["properties", "listings", "real-estate"],
    complexity: "advanced"
  },
  {
    id: "template_004",
    name: "Social Media Profiles",
    description: "Extract public profile information and engagement metrics",
    category: "Social Media",
    icon: Users,
    isStarred: false,
    isPublic: true,
    author: "Community",
    lastModified: "2024-01-12",
    usageCount: 692,
    successRate: 87.3,
    fields: ["username", "bio", "followers", "following", "posts"],
    tags: ["social", "profiles", "engagement"],
    complexity: "intermediate"
  },
  {
    id: "template_005",
    name: "Directory Listings",
    description: "Business directory scraper with contact details and ratings",
    category: "Business",
    icon: Globe,
    isStarred: false,
    isPublic: true,
    author: "System",
    lastModified: "2024-01-11",
    usageCount: 334,
    successRate: 91.7,
    fields: ["name", "address", "phone", "website", "rating", "reviews"],
    tags: ["directory", "business", "contacts"],
    complexity: "beginner"
  }
];

const categoryConfig = {
  "E-commerce": { color: "blue", icon: ShoppingBag },
  "Content": { color: "green", icon: Newspaper },
  "Real Estate": { color: "purple", icon: Building },
  "Social Media": { color: "pink", icon: Users },
  "Business": { color: "orange", icon: Globe }
};

const complexityConfig = {
  beginner: { color: "green", label: "Beginner" },
  intermediate: { color: "yellow", label: "Intermediate" },
  advanced: { color: "red", label: "Advanced" }
};

export default function TemplatesPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedComplexity, setSelectedComplexity] = useState("all");
  const [viewMode, setViewMode] = useState("grid");

  const filteredTemplates = mockTemplates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCategory = selectedCategory === "all" || template.category === selectedCategory;
    const matchesComplexity = selectedComplexity === "all" || template.complexity === selectedComplexity;
    return matchesSearch && matchesCategory && matchesComplexity;
  });

  const toggleStar = (templateId: string) => {
    // Mock star toggle - in real app would update backend
    console.log(`Toggle star for template ${templateId}`);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Templates</h1>
          <p className="text-gray-600 dark:text-gray-400">Create, manage, and use crawling templates</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Import
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            New Template
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-primary">{mockTemplates.length}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Templates</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
              {mockTemplates.filter(t => t.isStarred).length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Starred</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {mockTemplates.filter(t => t.isPublic).length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Public</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {mockTemplates.reduce((sum, t) => sum + t.usageCount, 0).toLocaleString()}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Uses</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4 space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search templates by name, description, or tags..."
              className="pl-10"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {/* Filter Tabs */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <Tabs value={selectedCategory} onValueChange={setSelectedCategory}>
                <TabsList className="grid w-full grid-cols-6">
                  <TabsTrigger value="all">All</TabsTrigger>
                  <TabsTrigger value="E-commerce">E-comm</TabsTrigger>
                  <TabsTrigger value="Content">Content</TabsTrigger>
                  <TabsTrigger value="Real Estate">Real Estate</TabsTrigger>
                  <TabsTrigger value="Social Media">Social</TabsTrigger>
                  <TabsTrigger value="Business">Business</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>

            <Tabs value={selectedComplexity} onValueChange={setSelectedComplexity} className="w-auto">
              <TabsList>
                <TabsTrigger value="all">All Levels</TabsTrigger>
                <TabsTrigger value="beginner">Beginner</TabsTrigger>
                <TabsTrigger value="intermediate">Intermediate</TabsTrigger>
                <TabsTrigger value="advanced">Advanced</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </CardContent>
      </Card>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTemplates.map((template) => {
          const CategoryIcon = template.icon;
          const categoryStyle = categoryConfig[template.category as keyof typeof categoryConfig];
          const complexityStyle = complexityConfig[template.complexity as keyof typeof complexityConfig];

          return (
            <Card key={template.id} className="hover:shadow-lg transition-shadow cursor-pointer group">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg bg-${categoryStyle.color}-100 dark:bg-${categoryStyle.color}-900/20`}>
                      <CategoryIcon className={`h-5 w-5 text-${categoryStyle.color}-600 dark:text-${categoryStyle.color}-400`} />
                    </div>
                    <div className="flex-1">
                      <CardTitle className="text-lg line-clamp-1">{template.name}</CardTitle>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline" className="text-xs">
                          {template.category}
                        </Badge>
                        <Badge 
                          variant={complexityStyle.color === "green" ? "default" : "secondary"} 
                          className="text-xs"
                        >
                          {complexityStyle.label}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleStar(template.id);
                    }}
                    className="text-gray-400 hover:text-yellow-500"
                  >
                    {template.isStarred ? (
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    ) : (
                      <StarOff className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <CardDescription className="line-clamp-2">
                  {template.description}
                </CardDescription>

                {/* Stats */}
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                  <span>{template.usageCount} uses</span>
                  <span>{template.successRate}% success</span>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-1">
                  {template.tags.slice(0, 3).map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                  {template.tags.length > 3 && (
                    <Badge variant="secondary" className="text-xs">
                      +{template.tags.length - 3}
                    </Badge>
                  )}
                </div>

                {/* Fields Preview */}
                <div className="space-y-1">
                  <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Fields ({template.fields.length})
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 line-clamp-1">
                    {template.fields.join(", ")}
                  </div>
                </div>

                {/* Meta Info */}
                <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 pt-2 border-t">
                  <div className="flex items-center gap-2">
                    <span>by {template.author}</span>
                    {template.isPublic && (
                      <Badge variant="outline" className="text-xs">
                        Public
                      </Badge>
                    )}
                  </div>
                  <span>{template.lastModified}</span>
                </div>

                {/* Actions */}
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity pt-2">
                  <Button size="sm" className="flex-1">
                    <Play className="h-3 w-3 mr-1" />
                    Use
                  </Button>
                  <Button variant="outline" size="sm">
                    <Eye className="h-3 w-3" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Copy className="h-3 w-3" />
                  </Button>
                  {template.author === "You" && (
                    <Button variant="outline" size="sm">
                      <Edit className="h-3 w-3" />
                    </Button>
                  )}
                  <Button variant="outline" size="sm">
                    <MoreHorizontal className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {filteredTemplates.length === 0 && (
        <Card>
          <CardContent className="p-12 text-center">
            <div className="text-gray-400 dark:text-gray-600">
              <Search className="h-12 w-12 mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">No templates found</h3>
              <p className="mb-4">Try adjusting your search or filter criteria</p>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create New Template
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
