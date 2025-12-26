import { useState, useEffect } from "react";
import { ShoppingCart, ExternalLink, Check, Copy, Package } from "lucide-react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Checkbox } from "./ui/checkbox";
import { Badge } from "./ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ShoppingList = ({ projectId, onComponentsSelected }) => {
  const [hardware, setHardware] = useState(null);
  const [selected, setSelected] = useState([]);
  const [shoppingList, setShoppingList] = useState(null);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const fetchHardware = async () => {
      try {
        const response = await axios.get(`${API}/hardware`);
        setHardware(response.data);
      } catch (err) {
        console.error("Failed to fetch hardware:", err);
      }
    };
    fetchHardware();
  }, []);

  const toggleComponent = (id) => {
    setSelected(prev => 
      prev.includes(id) 
        ? prev.filter(i => i !== id) 
        : [...prev, id]
    );
  };

  const generateList = async () => {
    if (selected.length === 0) {
      toast.error("Please select at least one component");
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.post(`${API}/shopping-list`, {
        component_ids: selected
      });
      setShoppingList(response.data);
      if (onComponentsSelected) {
        onComponentsSelected(selected);
      }
    } catch (err) {
      console.error("Failed to generate shopping list:", err);
      toast.error("Failed to generate shopping list");
    } finally {
      setLoading(false);
    }
  };

  const copyListAsText = async () => {
    if (!shoppingList) return;
    
    const text = shoppingList.components.map(c => 
      `- ${c.name} (${c.price_estimate})`
    ).join('\n');
    
    const fullText = `ESP32 IoT Project Shopping List\n${'='.repeat(30)}\n\n${text}\n\nEstimated Total: ${shoppingList.total_estimate}`;
    
    try {
      await navigator.clipboard.writeText(fullText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      toast.success("Shopping list copied!");
    } catch (err) {
      toast.error("Failed to copy");
    }
  };

  if (!hardware) return null;

  const categories = [
    { key: "boards", title: "Development Boards & Essentials", icon: "🔌" },
    { key: "sensors", title: "Sensors", icon: "📡" },
    { key: "displays", title: "Displays", icon: "📺" },
    { key: "actuators", title: "Actuators & Output", icon: "⚡" },
  ];

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button 
          variant="outline" 
          className="gap-2"
          data-testid="shopping-list-btn"
        >
          <ShoppingCart size={16} />
          Shopping List
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto bg-neutral-900 border-white/10">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 font-heading">
            <Package className="text-primary" size={20} />
            Hardware Shopping List Generator
          </DialogTitle>
        </DialogHeader>

        {!shoppingList ? (
          <div className="space-y-6">
            <p className="text-sm text-neutral-400">
              Select the components you need for your project. We'll generate a shopping list with links to Amazon and AliExpress.
            </p>

            {categories.map(category => {
              const items = hardware[category.key] || [];
              if (items.length === 0) return null;
              
              return (
                <div key={category.key}>
                  <h3 className="text-sm font-medium text-neutral-300 mb-3 flex items-center gap-2">
                    <span>{category.icon}</span>
                    {category.title}
                  </h3>
                  <div className="grid gap-2">
                    {items.map(item => (
                      <div
                        key={item.id}
                        className={`flex items-start gap-3 p-3 rounded-lg border transition-colors cursor-pointer ${
                          selected.includes(item.id)
                            ? "bg-primary/10 border-primary/30"
                            : "bg-neutral-800/50 border-white/5 hover:border-white/10"
                        }`}
                        onClick={() => toggleComponent(item.id)}
                        data-testid={`component-${item.id}`}
                      >
                        <Checkbox 
                          checked={selected.includes(item.id)}
                          onCheckedChange={() => toggleComponent(item.id)}
                          className="mt-1"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-medium text-neutral-200">{item.name}</span>
                            <Badge variant="outline" className="text-xs bg-emerald-500/10 text-emerald-400 border-emerald-500/30">
                              {item.price_estimate}
                            </Badge>
                          </div>
                          <p className="text-xs text-neutral-500 mt-1">{item.type}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}

            <div className="flex items-center justify-between pt-4 border-t border-white/10">
              <span className="text-sm text-neutral-400">
                {selected.length} component{selected.length !== 1 ? 's' : ''} selected
              </span>
              <Button
                onClick={generateList}
                disabled={selected.length === 0 || loading}
                className="bg-primary text-black hover:bg-primary/90"
                data-testid="generate-list-btn"
              >
                {loading ? "Generating..." : "Generate Shopping List"}
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30">
                {shoppingList.component_count} items • {shoppingList.total_estimate}
              </Badge>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={copyListAsText}
                  data-testid="copy-list-btn"
                >
                  {copied ? <Check size={14} /> : <Copy size={14} />}
                  <span className="ml-2">{copied ? "Copied!" : "Copy List"}</span>
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShoppingList(null)}
                >
                  Edit Selection
                </Button>
              </div>
            </div>

            <div className="space-y-3">
              {shoppingList.components.map(component => (
                <Card 
                  key={component.id}
                  className="bg-neutral-800/50 border-white/5 p-4"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h4 className="font-medium text-neutral-200">{component.name}</h4>
                      <p className="text-xs text-neutral-500 mt-1">{component.type}</p>
                      {component.notes && (
                        <p className="text-xs text-neutral-400 mt-2">{component.notes}</p>
                      )}
                    </div>
                    <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/30 shrink-0">
                      {component.price_estimate}
                    </Badge>
                  </div>
                  
                  <div className="flex gap-2 mt-3">
                    {component.shopping_links?.amazon && (
                      <a
                        href={component.shopping_links.amazon}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-xs text-orange-400 hover:text-orange-300 transition-colors"
                        data-testid={`amazon-link-${component.id}`}
                      >
                        <ExternalLink size={12} />
                        Amazon
                      </a>
                    )}
                    {component.shopping_links?.aliexpress && (
                      <a
                        href={component.shopping_links.aliexpress}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-xs text-red-400 hover:text-red-300 transition-colors"
                        data-testid={`aliexpress-link-${component.id}`}
                      >
                        <ExternalLink size={12} />
                        AliExpress
                      </a>
                    )}
                  </div>
                </Card>
              ))}
            </div>

            <Card className="bg-primary/5 border-primary/20 p-4">
              <div className="flex items-center justify-between">
                <span className="text-neutral-300 font-medium">Estimated Total</span>
                <span className="text-xl font-bold text-primary">{shoppingList.total_estimate}</span>
              </div>
              <p className="text-xs text-neutral-500 mt-2">
                Prices are estimates and may vary. Always compare prices across vendors.
              </p>
            </Card>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default ShoppingList;
